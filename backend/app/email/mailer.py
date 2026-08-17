"""SMTP dispatch with a small retry-with-backoff wrapper.

Simplification vs. NFR-6: this retries in-process from a FastAPI
BackgroundTask rather than a durable queue (Celery/SQS/etc). If the process
restarts mid-retry, or all attempts fail, the send is lost — acceptable for
this build but worth hardening with a real queue before high-volume
production use.
"""

import asyncio
import logging

import aiosmtplib
from email.message import EmailMessage

from app.core.config import get_settings

logger = logging.getLogger("learnflow.email")

_MAX_ATTEMPTS = 3
_BACKOFF_BASE_SEC = 2


async def _send_once(to: str, subject: str, body: str) -> None:
    settings = get_settings()
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user or None,
        password=settings.smtp_password or None,
        start_tls=settings.smtp_use_tls,
        timeout=settings.smtp_timeout_sec,
    )


async def send_email(to: str, subject: str, body: str) -> None:
    """Fire-and-forget-safe: never raises, logs and retries internally."""
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            await _send_once(to, subject, body)
            return
        except Exception as exc:  # noqa: BLE001 - best-effort dispatch, never crash the request
            logger.warning("email send attempt %s/%s to %s failed: %s", attempt, _MAX_ATTEMPTS, to, exc)
            if attempt < _MAX_ATTEMPTS:
                await asyncio.sleep(_BACKOFF_BASE_SEC * attempt)
    logger.error("email to %s permanently failed after %s attempts: %s", to, _MAX_ATTEMPTS, subject)
