"""Stateless JWT access tokens and opaque refresh-token primitives.

Refresh tokens are random opaque values; only their SHA-256 hash is ever
persisted (NFR-1, EC-X-11). Access tokens are short-lived JWTs carrying
role/status so authorization checks don't need a DB round trip for the
common case (EC-T-08 still re-checks live status from the DB on top of this).
"""

import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings


class TokenError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)


def create_access_token(*, user_id: uuid.UUID, role: str, status: str) -> tuple[str, datetime, str]:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=settings.access_token_ttl_min)
    jti = uuid.uuid4().hex
    payload = {
        "sub": str(user_id),
        "role": role,
        "status": status,
        "iat": now,
        "exp": exp,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "jti": jti,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token, exp, jti


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience,
            issuer=settings.jwt_issuer,
            leeway=settings.clock_skew_leeway_sec,
        )
    except jwt.ExpiredSignatureError as exc:
        raise TokenError("token_expired", "Access token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenError("token_invalid", "Access token is invalid.") from exc
    return payload


def generate_opaque_token() -> tuple[str, str]:
    """Returns (plaintext, sha256_hex_hash). >=256 bits of entropy (EC-13)."""
    plaintext = secrets.token_urlsafe(48)
    return plaintext, hash_opaque_token(plaintext)


def hash_opaque_token(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()
