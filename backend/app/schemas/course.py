import uuid

from pydantic import BaseModel, Field, field_validator

from app.models.course import CourseLevel
from app.models.lesson import LessonType
from app.models.quiz import QuestionType


def _validate_video_url(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    if not value.startswith("http://") and not value.startswith("https://"):
        raise ValueError("video_url must be an http:// or https:// URL")
    return value


# ---------- lessons ----------
class LessonOut(BaseModel):
    id: uuid.UUID
    title: str
    type: LessonType
    duration: int
    body: str
    video_url: str | None = None
    done: bool = False

    model_config = {"from_attributes": True}


class LessonIn(BaseModel):
    id: uuid.UUID | None = None
    title: str = Field(min_length=1, max_length=200)
    type: LessonType
    duration: int = Field(ge=1, le=600)
    body: str = ""
    video_url: str | None = Field(default=None, max_length=1000)

    _validate_video_url = field_validator("video_url")(_validate_video_url)


# ---------- quiz ----------
class QuizQuestionOut(BaseModel):
    """Learner-facing: never includes the answer."""

    id: uuid.UUID
    type: QuestionType
    text: str
    options: list[str] | None = None


class QuizQuestionInstructorOut(QuizQuestionOut):
    answer: bool | int | str


class QuizQuestionIn(BaseModel):
    id: uuid.UUID | None = None
    type: QuestionType
    text: str = Field(min_length=1, max_length=500)
    options: list[str] | None = None
    answer: bool | int | str


class QuizAnswerItem(BaseModel):
    question_id: uuid.UUID
    value: str


class QuizSubmitRequest(BaseModel):
    answers: list[QuizAnswerItem]


class QuizReviewItem(BaseModel):
    text: str
    given: str
    correct: str
    ok: bool


class QuizSubmitResponse(BaseModel):
    score: int
    correct_count: int
    total_count: int
    passed: bool
    review: list[QuizReviewItem]


# ---------- courses ----------
class CourseListItem(BaseModel):
    id: uuid.UUID
    title: str
    category: str
    level: CourseLevel
    instructor_name: str
    rating: float | None
    students: int
    duration_hrs: int
    swatch: int
    lesson_count: int
    enrolled: bool = False
    progress_pct: int = 0


class CourseDetail(CourseListItem):
    description: str
    lessons: list[LessonOut]
    has_quiz: bool
    quiz_question_count: int
    quiz_attempted: bool = False
    quiz_best_score: int | None = None
    done_count: int = 0


class CourseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=100)
    level: CourseLevel = CourseLevel.beginner
    instructor_name: str = Field(min_length=1, max_length=200)
    duration_hrs: int = Field(ge=1, le=500)
    rating: float | None = None
    swatch: int = 0
    description: str = ""
    lessons: list[LessonIn] = []
    quiz_questions: list[QuizQuestionIn] = []


class CourseUpdate(CourseCreate):
    pass


class InstructorCourseListItem(BaseModel):
    id: uuid.UUID
    title: str
    students: int
    completion_rate: int
    avg_quiz_score: int
    rating: float | None
    swatch: int


# ---------- dashboard / analytics ----------
class DashboardStats(BaseModel):
    stat_enrolled: int
    stat_completed: int
    stat_avg_score: int
    stat_certificates: int


class EnrolledCourseOut(BaseModel):
    id: uuid.UUID
    title: str
    swatch: int
    progress_pct: int
    done_count: int
    lesson_total: int
    quiz_attempted: bool
    quiz_score: int | None
    has_certificate: bool


class DashboardOut(BaseModel):
    stats: DashboardStats
    enrolled_courses: list[EnrolledCourseOut]


class AnalyticsCourseRow(BaseModel):
    id: uuid.UUID
    title: str
    students: int
    completion_rate: int
    avg_quiz_score: int
    rating: float | None


class AnalyticsOut(BaseModel):
    total_students: int
    avg_completion_rate: int
    avg_quiz_score_all: int
    courses: list[AnalyticsCourseRow]
