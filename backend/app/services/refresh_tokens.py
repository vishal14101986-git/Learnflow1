"""Refresh-token issue/rotate/revoke with reuse (theft) detection.

EC-T-04: presenting an already-rotated token revokes the whole token family.
EC-T-05 (two tabs racing a refresh at once) is handled client-side instead of
with a server-side grace window: the frontend single-flights concurrent
refresh calls into one in-flight request (see frontend/src/lib/api.ts), which
the BRD itself lists as an acceptable alternative to a grace window. That
keeps this rotation logic strictly single-use, which is the safer default.
"""

import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.token import RefreshToken
from app.security.tokens import generate_opaque_token, hash_opaque_token


class RefreshTokenError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


async def issue(db: AsyncSession, *, user_id: uuid.UUID, ip: str | None, family_id: uuid.UUID | None = None) -> tuple[str, RefreshToken]:
    settings = get_settings()
    plaintext, digest = generate_opaque_token()
    now = datetime.now(timezone.utc)
    row = RefreshToken(
        family_id=family_id or uuid.uuid4(),
        user_id=user_id,
        token_hash=digest,
        expires_at=now + timedelta(days=settings.refresh_token_ttl_days),
        ip=ip,
    )
    db.add(row)
    await db.flush()
    return plaintext, row


async def revoke_family(db: AsyncSession, family_id: uuid.UUID) -> None:
    now = datetime.now(timezone.utc)
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=now)
    )


async def revoke_all_for_user(db: AsyncSession, user_id: uuid.UUID, *, except_id: uuid.UUID | None = None) -> None:
    now = datetime.now(timezone.utc)
    stmt = update(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
    if except_id is not None:
        stmt = stmt.where(RefreshToken.id != except_id)
    await db.execute(stmt.values(revoked_at=now))


async def rotate(db: AsyncSession, plaintext: str, *, ip: str | None) -> tuple[str, RefreshToken]:
    """Validates the presented refresh token and issues a replacement.

    Raises RefreshTokenError with code:
      - "invalid": no matching token on record
      - "expired": token existed but is past its TTL
      - "reused": token was already rotated/revoked before — the whole
        family has now been revoked and the caller must sign in again.
    """
    digest = hash_opaque_token(plaintext)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == digest))
    row = result.scalar_one_or_none()
    if row is None:
        raise RefreshTokenError("invalid", "Refresh token is invalid.")

    now = datetime.now(timezone.utc)

    if row.revoked_at is not None:
        # Reuse of an already-rotated (or already-revoked) token: treat as theft.
        await revoke_family(db, row.family_id)
        raise RefreshTokenError("reused", "This session has been revoked for your security. Please sign in again.")

    if row.expires_at < now:
        raise RefreshTokenError("expired", "Your session has expired. Please sign in again.")

    new_plaintext, new_row = await issue(db, user_id=row.user_id, ip=ip, family_id=row.family_id)
    row.revoked_at = now
    row.replaced_by_id = new_row.id
    await db.flush()
    return new_plaintext, new_row
