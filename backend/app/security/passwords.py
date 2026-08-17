"""Password hashing and policy enforcement (BRD BR-1, Appendix A.2).

The common-password list here is a small curated set for local, offline
screening. It approximates but does not replace a live breached-password
service (e.g. Have I Been Pwned's k-anonymity API) — swap
`is_commonly_breached` for a real lookup before relying on this in
production.
"""

import unicodedata
from functools import lru_cache
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import get_settings

_hasher = PasswordHasher()
_COMMON_PASSWORDS_PATH = Path(__file__).parent / "common_passwords.txt"


@lru_cache
def _common_passwords() -> frozenset[str]:
    text = _COMMON_PASSWORDS_PATH.read_text(encoding="utf-8")
    return frozenset(line.strip().lower() for line in text.splitlines() if line.strip())


def normalize(raw: str) -> str:
    """NFKC-normalize then trim surrounding whitespace (EC-P-04, EC-P-06)."""
    return unicodedata.normalize("NFKC", raw).strip()


class PasswordPolicyError(ValueError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


def validate_password_policy(raw_password: str, *, email: str | None = None, name: str | None = None) -> str:
    """Validates policy and returns the normalized password to hash.

    Raises PasswordPolicyError with a specific, user-facing message on failure.
    """
    settings = get_settings()

    # EC-P-05: reject excessive length before any normalization/hashing work.
    if len(raw_password) > 5000:
        raise PasswordPolicyError(f"Password must be no more than {settings.password_max_length} characters.")

    normalized = normalize(raw_password)

    if len(normalized) > settings.password_max_length:
        raise PasswordPolicyError(f"Password must be no more than {settings.password_max_length} characters.")

    if len(normalized) < settings.password_min_length:
        raise PasswordPolicyError(f"Password must be at least {settings.password_min_length} characters.")

    if normalized.lower() in _common_passwords():
        raise PasswordPolicyError(
            "This password has appeared in known data breaches and cannot be used. Please choose another."
        )

    lowered = normalized.lower()
    if email:
        local_part = email.split("@", 1)[0].strip().lower()
        if local_part and len(local_part) >= 3 and local_part in lowered:
            raise PasswordPolicyError("Password cannot contain your email address.")
    if name:
        name_norm = name.strip().lower()
        if name_norm and len(name_norm) >= 3 and name_norm in lowered:
            raise PasswordPolicyError("Password cannot contain your name.")

    return normalized


def hash_password(raw_password: str) -> str:
    normalized = normalize(raw_password)
    return _hasher.hash(normalized)


def verify_password(raw_password: str, password_hash: str) -> bool:
    normalized = normalize(raw_password)
    try:
        return _hasher.verify(password_hash, normalized)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


# A pre-computed hash of a random value, used to perform a dummy verify so
# that sign-in timing for a non-existent account matches a real one (EC-C-02).
_DUMMY_HASH = _hasher.hash("dummy-value-for-constant-time-comparison-only")


def dummy_verify() -> None:
    try:
        _hasher.verify(_DUMMY_HASH, "irrelevant-input")
    except VerifyMismatchError:
        pass
