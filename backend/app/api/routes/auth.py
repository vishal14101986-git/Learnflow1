from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_client_ip, get_current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models.token import RefreshToken, RevokedAccessToken
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    GenericMessage,
    LoginRequest,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
)
from app.security.rate_limit import limiter
from app.security.tokens import decode_access_token, hash_opaque_token
from app.services import auth_service
from app.services.refresh_tokens import RefreshTokenError

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "lf_refresh_token"


def _set_refresh_cookie(response: Response, plaintext: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=plaintext,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.refresh_token_ttl_days * 24 * 3600,
        path="/auth",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/auth")


def _token_response(access_token: str, exp: datetime, user: User) -> TokenResponse:
    expires_in = max(0, int((exp - datetime.now(timezone.utc)).total_seconds()))
    return TokenResponse(access_token=access_token, expires_in=expires_in, user=UserOut.model_validate(user))


REGISTER_MESSAGE = "If that email address is available, we've created your account — check your inbox for a verification link."
RESEND_MESSAGE = "If that account needs verification, we've sent a new link."
FORGOT_MESSAGE = "If an account exists for that address, we've sent password reset instructions."


@router.post("/register", response_model=GenericMessage, status_code=status.HTTP_201_CREATED)
@limiter.limit(get_settings().register_rate_limit)
async def register(
    request: Request,
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> GenericMessage:
    await auth_service.register(
        db,
        background_tasks,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        confirm_password=payload.confirm_password,
        role=payload.role,
        ip=get_client_ip(request),
    )
    await db.commit()
    return GenericMessage(message=REGISTER_MESSAGE)


@router.get("/verify-email", response_model=GenericMessage)
async def verify_email(token: str, db: AsyncSession = Depends(get_db)) -> GenericMessage:
    try:
        await auth_service.verify_email(db, token)
    except auth_service.AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    await db.commit()
    return GenericMessage(message="Your email address has been verified. You can now sign in.")


@router.post("/verify-email/resend", response_model=GenericMessage)
async def resend_verification(
    payload: ResendVerificationRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> GenericMessage:
    await auth_service.resend_verification(db, background_tasks, email=payload.email, ip=get_client_ip(request))
    await db.commit()
    return GenericMessage(message=RESEND_MESSAGE)


@router.post("/login", response_model=TokenResponse)
@limiter.limit(get_settings().login_rate_limit)
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    try:
        access_token, exp, refresh_plaintext, _jti, user = await auth_service.login(
            db, background_tasks, email=payload.email, password=payload.password, ip=get_client_ip(request)
        )
    except auth_service.AuthError as exc:
        await db.commit()  # persist failed-attempt / lockout bookkeeping even on failure
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message) from exc

    await db.commit()
    _set_refresh_cookie(response, refresh_plaintext)
    return _token_response(access_token, exp, user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    refresh_plaintext = request.cookies.get(REFRESH_COOKIE_NAME)
    if not refresh_plaintext:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No active session.")

    try:
        access_token, exp, new_refresh_plaintext, user = await auth_service.refresh_session(
            db, refresh_plaintext=refresh_plaintext, ip=get_client_ip(request)
        )
    except RefreshTokenError as exc:
        await db.commit()
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message) from exc
    except auth_service.AuthError as exc:
        await db.commit()
        _clear_refresh_cookie(response)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message) from exc

    await db.commit()
    _set_refresh_cookie(response, new_refresh_plaintext)
    return _token_response(access_token, exp, user)


@router.post("/logout", response_model=GenericMessage)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)) -> GenericMessage:
    refresh_plaintext = request.cookies.get(REFRESH_COOKIE_NAME)
    await auth_service.logout(db, refresh_plaintext=refresh_plaintext)

    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        try:
            payload = decode_access_token(auth_header[7:].strip())
            exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            db.add(RevokedAccessToken(jti=payload["jti"], expires_at=exp))
        except Exception:  # noqa: BLE001 - best-effort; logout must still succeed
            pass

    await db.commit()
    _clear_refresh_cookie(response)
    return GenericMessage(message="You have been signed out.")


@router.post("/logout-all", response_model=GenericMessage)
async def logout_all(
    response: Response, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
) -> GenericMessage:
    await auth_service.logout_all(db, user.id)
    await db.commit()
    _clear_refresh_cookie(response)
    return GenericMessage(message="You have been signed out on all devices.")


@router.post("/forgot-password", response_model=GenericMessage)
@limiter.limit(get_settings().forgot_password_rate_limit)
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> GenericMessage:
    await auth_service.forgot_password(db, background_tasks, email=payload.email, ip=get_client_ip(request))
    await db.commit()
    return GenericMessage(message=FORGOT_MESSAGE)


@router.post("/reset-password", response_model=GenericMessage)
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> GenericMessage:
    try:
        await auth_service.reset_password(
            db,
            background_tasks,
            token=payload.token,
            new_password=payload.new_password,
            confirm_password=payload.confirm_password,
            ip=get_client_ip(request),
        )
    except (auth_service.AuthError,) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    await db.commit()
    return GenericMessage(message="Your password has been reset. You can now sign in.")


@router.post("/change-password", response_model=GenericMessage)
async def change_password(
    request: Request,
    payload: ChangePasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> GenericMessage:
    keep_id = None
    refresh_plaintext = request.cookies.get(REFRESH_COOKIE_NAME)
    if refresh_plaintext:
        digest = hash_opaque_token(refresh_plaintext)
        result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == digest))
        row = result.scalar_one_or_none()
        keep_id = row.id if row else None

    try:
        await auth_service.change_password(
            db,
            background_tasks,
            user=user,
            current_password=payload.current_password,
            new_password=payload.new_password,
            confirm_password=payload.confirm_password,
            keep_refresh_token_id=keep_id,
            ip=get_client_ip(request),
        )
    except auth_service.AuthError as exc:
        await db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    await db.commit()
    return GenericMessage(message="Your password has been changed.")


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)
