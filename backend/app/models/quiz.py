import enum
import uuid

from sqlalchemy import JSON, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import UUIDPkMixin


class QuestionType(str, enum.Enum):
    mcq = "mcq"
    tf = "tf"
    short = "short"


class QuizQuestion(UUIDPkMixin, Base):
    __tablename__ = "quiz_questions"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False
    )
    type: Mapped[QuestionType] = mapped_column(Enum(QuestionType, native_enum=False, length=16), nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    options: Mapped[list | None] = mapped_column(JSON, nullable=True)
    answer: Mapped[bool | int | str] = mapped_column(JSON, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    course: Mapped["Course"] = relationship(back_populates="quiz_questions")  # noqa: F821
