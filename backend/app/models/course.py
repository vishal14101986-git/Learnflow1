import enum
import uuid

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPkMixin


class CourseLevel(str, enum.Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"


class Course(UUIDPkMixin, TimestampMixin, Base):
    __tablename__ = "courses"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    level: Mapped[CourseLevel] = mapped_column(Enum(CourseLevel, native_enum=False, length=32), nullable=False)

    instructor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    instructor_name: Mapped[str] = mapped_column(String(200), nullable=False)

    duration_hrs: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    swatch: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", order_by="Lesson.order_index"
    )
    quiz_questions: Mapped[list["QuizQuestion"]] = relationship(
        back_populates="course", cascade="all, delete-orphan", order_by="QuizQuestion.order_index"
    )
