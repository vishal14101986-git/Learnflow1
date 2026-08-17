"""Plain-text email bodies. Kept as simple functions rather than a template
engine round-trip to disk, since every message here is a handful of lines."""

from app.core.config import get_settings


def _base_url() -> str:
    return get_settings().frontend_base_url.rstrip("/")


def verification_email(*, name: str, token: str) -> tuple[str, str]:
    link = f"{_base_url()}/verify-email?token={token}"
    subject = "Verify your LearnFlow email address"
    body = (
        f"Hi {name},\n\n"
        f"Thanks for registering with LearnFlow. Please confirm your email address by opening the link below "
        f"within the next 24 hours:\n\n{link}\n\n"
        f"If you didn't create this account, you can ignore this email.\n\nLearnFlow"
    )
    return subject, body


def duplicate_registration_email(*, name: str) -> tuple[str, str]:
    link = f"{_base_url()}/login"
    reset_link = f"{_base_url()}/forgot-password"
    subject = "Someone tried to register with your LearnFlow email"
    body = (
        f"Hi {name},\n\n"
        f"Someone just tried to create a new LearnFlow account using your email address. Your existing account "
        f"is unaffected.\n\nIf this was you, you can sign in here:\n{link}\n\n"
        f"Forgot your password? Reset it here:\n{reset_link}\n\n"
        f"If this wasn't you, no action is needed.\n\nLearnFlow"
    )
    return subject, body


def deactivated_duplicate_email(*, name: str) -> tuple[str, str]:
    subject = "Account reactivation — LearnFlow"
    body = (
        f"Hi {name},\n\n"
        f"Someone tried to register a new LearnFlow account with your email address, which belongs to a "
        f"deactivated account. If you'd like to reactivate it, please contact support.\n\nLearnFlow"
    )
    return subject, body


def password_reset_email(*, name: str, token: str) -> tuple[str, str]:
    link = f"{_base_url()}/reset-password?token={token}"
    subject = "Reset your LearnFlow password"
    body = (
        f"Hi {name},\n\n"
        f"We received a request to reset your LearnFlow password. This link is valid for 30 minutes and can "
        f"only be used once:\n\n{link}\n\n"
        f"If you didn't request this, you can safely ignore this email — your password will not change.\n\n"
        f"LearnFlow"
    )
    return subject, body


def suspended_account_reset_email(*, name: str) -> tuple[str, str]:
    subject = "LearnFlow account access"
    body = (
        f"Hi {name},\n\n"
        f"A password reset was requested for your account, but it is currently suspended. Please contact "
        f"support for help regaining access.\n\nLearnFlow"
    )
    return subject, body


def security_lockout_email(*, name: str) -> tuple[str, str]:
    subject = "LearnFlow security alert: your account was temporarily locked"
    body = (
        f"Hi {name},\n\n"
        f"We locked your LearnFlow account for 15 minutes after several failed sign-in attempts. If this "
        f"wasn't you, consider resetting your password once the lock clears.\n\nLearnFlow"
    )
    return subject, body


def password_changed_email(*, name: str) -> tuple[str, str]:
    subject = "Your LearnFlow password was changed"
    body = (
        f"Hi {name},\n\n"
        f"This confirms your LearnFlow password was just changed. All other sessions have been signed out. "
        f"If you didn't make this change, contact support immediately.\n\nLearnFlow"
    )
    return subject, body
