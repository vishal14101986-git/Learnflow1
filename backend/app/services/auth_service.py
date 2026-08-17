"""Registration, login, verification, and password-reset orchestration.

Each function implements the specific behaviours called out in
learnflow1-auth-brd.md (referenced in comments as US-AUTH-*, EC-*, BR-*).
"""

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks
from sqlalchemy import func, select
from sqlalchemy import update as sa_update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.email.mailer import send_email
from app.email.templates import (
    deactivated_duplicate_email,
    duplicate_registration_email,
    password_changed_email,
    password_reset_email,
    security_lockout_email,
    suspended_account_reset_email,
    verification_email,
)
from app.models.token import EmailVerificationToken, PasswordResetToken
from app.models.user import User, UserRole, UserStatus
from app.security.passwords import PasswordPolicyError, dummy_verify, hash_password, validate_password_policy, verify_password
from app.security.tokens import create_access_token, generate_opaque_token, hash_opaque_token
from app.services import refresh_tokens
from app.services.audit import log_event


class AuthError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def normalize_email(email: str) -> str:
    return email.strip().lower()


async def _get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


def _queue(background_tasks: BackgroundTasks, to: str, subject_body: tuple[str, str]) -> None:
    subject, body = subject_body
    background_tasks.add_task(send_email, to, subject, body)


async def _issue_verification_token(db: AsyncSession, user: User) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)

    # Invalidate any outstanding unused verification tokens (EC-X-09 style hygiene).
    outstanding = await db.execute(
        select(EmailVerificationToken).where(
            EmailVerificationToken.user_id == user.id, EmailVerificationToken.used_at.is_(None)
        )
    )
    for old in outstanding.scalars():
        old.used_at = now

    plaintext, digest = generate_opaque_token()
    db.add(
        EmailVerificationToken(
            user_id=user.id,
            token_hash=digest,
            expires_at=now + timedelta(hours=settings.verify_token_ttl_hours),
        )
    )
    await db.flush()
    return plaintext


async def register(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    *,
    name: str,
    email: str,
    password: str,
    confirm_password: str,
    role: UserRole,
    ip: str | None,
) -> None:
    normalized_email = normalize_email(email)
    name = name.strip()

    existing = await _get_user_by_email(db, normalized_email)

    if existing is not None:
        # EC-R-01..07: never create a second account, never reveal which branch fired.
        if existing.status == UserStatus.pending_verification:
            token = await _issue_verification_token(db, existing)
            _queue(background_tasks, existing.email, verification_email(name=existing.name, token=token))
            await log_event(db, event_type="register_duplicate_pending", email=normalized_email, ip=ip)
        elif existing.status == UserStatus.deactivated:
            _queue(background_tasks, existing.email, deactivated_duplicate_email(name=existing.name))
            await log_event(db, event_type="register_duplicate_deactivated", email=normalized_email, ip=ip)
        else:
            _queue(background_tasks, existing.email, duplicate_registration_email(name=existing.name))
            await log_event(db, event_type="register_duplicate_active", email=normalized_email, ip=ip)
        return

    if password != confirm_password:
        raise PasswordPolicyError("Passwords do not match.")

    normalized_password = validate_password_policy(password, email=normalized_email, name=name)

    user = User(
        email=normalized_email,
        name=name,
        password_hash=hash_password(normalized_password),
        role=role,
        status=UserStatus.pending_verification,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        # EC-R-05: unique-index race with a concurrent identical registration.
        await db.rollback()
        existing = await _get_user_by_email(db, normalized_email)
        if existing is not None:
            _queue(background_tasks, existing.email, duplicate_registration_email(name=existing.name))
            await log_event(db, event_type="register_duplicate_race", email=normalized_email, ip=ip)
            return
        raise

    token = await _issue_verification_token(db, user)
    _queue(background_tasks, user.email, verification_email(name=user.name, token=token))
    await log_event(db, event_type="register_success", user_id=user.id, email=normalized_email, ip=ip)


async def verify_email(db: AsyncSession, token: str) -> None:
    digest = hash_opaque_token(token)
    result = await db.execute(select(EmailVerificationToken).where(EmailVerificationToken.token_hash == digest))
    row = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if row is None or row.used_at is not None or row.expires_at < now:
        raise AuthError("verify_invalid", "This verification link is invalid or has expired. Request a new one.")

    result = await db.execute(select(User).where(User.id == row.user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthError("verify_invalid", "This verification link is invalid or has expired. Request a new one.")

    row.used_at = now
    if user.status == UserStatus.pending_verification:
        user.status = UserStatus.active
    await log_event(db, event_type="email_verified", user_id=user.id, email=user.email)


async def resend_verification(
    db: AsyncSession, background_tasks: BackgroundTasks, *, email: str, ip: str | None
) -> None:
    normalized_email = normalize_email(email)
    user = await _get_user_by_email(db, normalized_email)
    if user is None or user.status != UserStatus.pending_verification:
        return  # neutral no-op: don't reveal account existence or state

    settings = get_settings()
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    count_result = await db.execute(
        select(func.count())
        .select_from(EmailVerificationToken)
        .where(EmailVerificationToken.user_id == user.id, EmailVerificationToken.created_at >= one_hour_ago)
    )
    if count_result.scalar_one() >= settings.resend_verification_max_per_hour:
        return  # silently throttled

    token = await _issue_verification_token(db, user)
    _queue(background_tasks, user.email, verification_email(name=user.name, token=token))
    await log_event(db, event_type="verification_resent", user_id=user.id, email=normalized_email, ip=ip)


async def login(
    db: AsyncSession, background_tasks: BackgroundTasks, *, email: str, password: str, ip: str | None
) -> tuple[str, datetime, str, str, User]:
    """Returns (access_token, access_expires_at, refresh_plaintext, jti, user)."""
    settings = get_settings()
    normalized_email = normalize_email(email)
    user = await _get_user_by_email(db, normalized_email)
    now = datetime.now(timezone.utc)

    if user is None:
        dummy_verify()  # EC-C-02: constant-time-ish failure for nonexistent accounts
        await log_event(db, event_type="login_failed_no_account", email=normalized_email, ip=ip)
        raise AuthError("invalid_credentials", "Incorrect email or password.")

    if user.status == UserStatus.locked:
        if user.locked_until and user.locked_until > now:
            raise AuthError("account_locked", "Your account is temporarily locked. Try again in a few minutes.")
        # BR-5: lock self-clears once the window elapses.
        user.status = UserStatus.active
        user.failed_attempts = 0
        user.locked_until = None

    if user.status == UserStatus.pending_verification:
        raise AuthError("unverified", "Please verify your email address before signing in.")

    if user.status in (UserStatus.suspended, UserStatus.deactivated):
        raise AuthError("account_disabled", "Your account is not active. Please contact support.")

    if not verify_password(password, user.password_hash):
        user.failed_attempts += 1
        await log_event(db, event_type="login_failed_bad_password", user_id=user.id, email=normalized_email, ip=ip)
        if user.failed_attempts >= settings.lockout_threshold:
            user.status = UserStatus.locked
            user.locked_until = now + timedelta(minutes=settings.lockout_minutes)
            _queue(background_tasks, user.email, security_lockout_email(name=user.name))
            await log_event(db, event_type="account_locked", user_id=user.id, email=normalized_email, ip=ip)
        raise AuthError("invalid_credentials", "Incorrect email or password.")

    user.failed_attempts = 0
    user.last_login_at = now
    user.last_login_ip = ip

    access_token, exp, jti = create_access_token(user_id=user.id, role=user.role.value, status=user.status.value)
    refresh_plaintext, _ = await refresh_tokens.issue(db, user_id=user.id, ip=ip)
    await log_event(db, event_type="login_success", user_id=user.id, email=normalized_email, ip=ip)
    return access_token, exp, refresh_plaintext, jti, user


async def refresh_session(
    db: AsyncSession, *, refresh_plaintext: str, ip: str | None
) -> tuple[str, datetime, str, User]:
    row_plaintext, new_row = await refresh_tokens.rotate(db, refresh_plaintext, ip=ip)

    result = await db.execute(select(User).where(User.id == new_row.user_id))
    user = result.scalar_one_or_none()
    if user is None or user.status not in (UserStatus.active, UserStatus.locked):
        await refresh_tokens.revoke_family(db, new_row.family_id)
        raise AuthError("account_disabled", "Your account is not active. Please sign in again.")

    access_token, exp, _jti = create_access_token(user_id=user.id, role=user.role.value, status=user.status.value)
    return access_token, exp, row_plaintext, user


async def logout(db: AsyncSession, *, refresh_plaintext: str | None) -> None:
    if not refresh_plaintext:
        return
    digest = hash_opaque_token(refresh_plaintext)
    result = await db.execute(select(refresh_tokens.RefreshToken).where(refresh_tokens.RefreshToken.token_hash == digest))
    row = result.scalar_one_or_none()
    if row is not None and row.revoked_at is None:
        row.revoked_at = datetime.now(timezone.utc)


async def logout_all(db: AsyncSession, user_id: uuid.UUID) -> None:
    await refresh_tokens.revoke_all_for_user(db, user_id)


async def forgot_password(
    db: AsyncSession, background_tasks: BackgroundTasks, *, email: str, ip: str | None
) -> None:
    settings = get_settings()
    normalized_email = normalize_email(email)
    user = await _get_user_by_email(db, normalized_email)
    if user is None:
        return  # EC-X-01: byte-identical neutral response, nothing dispatched

    if user.status == UserStatus.pending_verification:
        token = await _issue_verification_token(db, user)
        _queue(background_tasks, user.email, verification_email(name=user.name, token=token))
        return

    if user.status == UserStatus.suspended:
        _queue(background_tasks, user.email, suspended_account_reset_email(name=user.name))
        return

    if user.status == UserStatus.deactivated:
        return  # no path back via self-service reset

    # active or locked
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    count_result = await db.execute(
        select(func.count())
        .select_from(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id, PasswordResetToken.created_at >= one_hour_ago)
    )
    if count_result.scalar_one() >= 3:
        return  # silently throttled

    now = datetime.now(timezone.utc)
    # EC-X-09: issuing a new token invalidates any earlier outstanding one.
    old_tokens = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.user_id == user.id, PasswordResetToken.used_at.is_(None))
    )
    for old in old_tokens.scalars():
        old.used_at = now

    plaintext, digest = generate_opaque_token()
    db.add(
        PasswordResetToken(
            user_id=user.id,
            token_hash=digest,
            expires_at=now + timedelta(minutes=settings.reset_token_ttl_min),
        )
    )
    _queue(background_tasks, user.email, password_reset_email(name=user.name, token=plaintext))
    await log_event(db, event_type="password_reset_requested", user_id=user.id, email=normalized_email, ip=ip)


async def reset_password(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    *,
    token: str,
    new_password: str,
    confirm_password: str,
    ip: str | None,
) -> None:
    if new_password != confirm_password:
        raise PasswordPolicyError("Passwords do not match.")

    digest = hash_opaque_token(token)
    result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.token_hash == digest))
    row = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if row is None or row.used_at is not None or row.expires_at < now:
        raise AuthError("reset_invalid", "This reset link is invalid or has expired. Please request a new one.")

    result = await db.execute(select(User).where(User.id == row.user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise AuthError("reset_invalid", "This reset link is invalid or has expired. Please request a new one.")

    normalized_password = validate_password_policy(new_password, email=user.email, name=user.name)

    if verify_password(normalized_password, user.password_hash):
        raise PasswordPolicyError("New password must be different from your current password.")

    # EC-X-13: atomic single-use consume — only one concurrent submission wins.
    consume_result = await db.execute(
        sa_update(PasswordResetToken)
        .where(PasswordResetToken.id == row.id, PasswordResetToken.used_at.is_(None))
        .values(used_at=now)
    )
    if consume_result.rowcount != 1:
        raise AuthError("reset_invalid", "This reset link is invalid or has expired. Please request a new one.")

    user.password_hash = hash_password(normalized_password)
    user.failed_attempts = 0
    if user.status == UserStatus.locked:
        user.status = UserStatus.active
        user.locked_until = None

    await refresh_tokens.revoke_all_for_user(db, user.id)
    _queue(background_tasks, user.email, password_changed_email(name=user.name))
    await log_event(db, event_type="password_reset_completed", user_id=user.id, email=user.email, ip=ip)


async def change_password(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    *,
    user: User,
    current_password: str,
    new_password: str,
    confirm_password: str,
    keep_refresh_token_id: uuid.UUID | None,
    ip: str | None,
) -> None:
    settings = get_settings()
    if not verify_password(current_password, user.password_hash):
        user.failed_attempts += 1
        if user.failed_attempts >= settings.lockout_threshold:
            user.status = UserStatus.locked
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=settings.lockout_minutes)
            _queue(background_tasks, user.email, security_lockout_email(name=user.name))
        raise AuthError("invalid_current_password", "Current password is incorrect.")

    if new_password != confirm_password:
        raise PasswordPolicyError("Passwords do not match.")

    normalized_password = validate_password_policy(new_password, email=user.email, name=user.name)

    if verify_password(normalized_password, user.password_hash):
        raise PasswordPolicyError("New password must be different from your current password.")

    user.password_hash = hash_password(normalized_password)
    user.failed_attempts = 0
    await refresh_tokens.revoke_all_for_user(db, user.id, except_id=keep_refresh_token_id)
    _queue(background_tasks, user.email, password_changed_email(name=user.name))
    await log_event(db, event_type="password_changed", user_id=user.id, email=user.email, ip=ip)
