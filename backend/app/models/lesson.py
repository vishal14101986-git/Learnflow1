import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import UUIDPkMixin


class LessonType(str, enum.Enum):
    video = "video"
    text = "text"


class Lesson(UUIDPkMixin, Base):
    __tablename__ = "lessons"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    type: Mapped[LessonType] = mapped_column(Enum(LessonType, native_enum=False, length=16), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    body: Mapped[str] = mapped_column(Text, default="", nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    course: Mapped["Course"] = relationship(back_populates="lessons")  # noqa: F821
