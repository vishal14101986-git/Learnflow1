import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


async def log_event(
    db: AsyncSession,
    *,
    event_type: str,
    user_id: uuid.UUID | None = None,
    email: str | None = None,
    ip: str | None = None,
    details: dict | None = None,
) -> None:
    db.add(AuditLog(event_type=event_type, user_id=user_id, email=email, ip=ip, details=details))
    await db.flush()
