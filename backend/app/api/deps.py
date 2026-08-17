import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.token import RevokedAccessToken
from app.models.user import User, UserStatus
from app.security.tokens import TokenError, decode_access_token


def get_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    auth_header = request.headers.get("authorization", "")
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = auth_header[7:].strip()

    try:
        payload = decode_access_token(token)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"X-Error-Code": exc.code},
        ) from exc

    jti = payload.get("jti")
    if jti:
        revoked = await db.execute(select(RevokedAccessToken).where(RevokedAccessToken.jti == jti))
        if revoked.scalar_one_or_none() is not None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="This session has been signed out.")

    try:
        user_id = uuid.UUID(payload.get("sub", ""))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated") from exc

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # EC-T-08: account status is re-checked live on every request, never inferred solely from the token.
    if user.status not in (UserStatus.active, UserStatus.locked):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account is not active.")

    # EC-T-09: role authorization is decided from the token's role claim (frozen at issuance),
    # not a live DB lookup, so a mid-session promotion only takes effect after the next refresh.
    request.state.token_role = payload.get("role")

    return user


def require_role(*roles: str) -> Callable:
    async def dependency(request: Request, user: User = Depends(get_current_user)) -> User:
        token_role = getattr(request.state, "token_role", None)
        if token_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return user

    return dependency
