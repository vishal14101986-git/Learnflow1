"""Course catalog, enrollment, lesson/quiz progress, instructor authoring,
and analytics — the LMS domain the design prototype (`LearnFlow.dc.html`)
depicts, backed by real persistence and per-instructor ownership instead of
the prototype's shared localStorage array.
"""

import uuid
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.lesson import Lesson
from app.models.progress import LessonCompletion, QuizAttempt
from app.models.quiz import QuizQuestion
from app.models.user import User
from app.schemas.course import (
    AnalyticsCourseRow,
    AnalyticsOut,
    CourseCreate,
    CourseDetail,
    CourseListItem,
    DashboardStats,
    EnrolledCourseOut,
    InstructorCourseListItem,
    LessonOut,
    QuizQuestionInstructorOut,
    QuizQuestionOut,
    QuizReviewItem,
    QuizSubmitRequest,
    QuizSubmitResponse,
)


class LmsError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


async def _get_course_or_404(db: AsyncSession, course_id: uuid.UUID) -> Course:
    result = await db.execute(
        select(Course)
        .options(selectinload(Course.lessons), selectinload(Course.quiz_questions))
        .where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    if course is None:
        raise LmsError("not_found", "Course not found.", status_code=404)
    return course


async def _students_count(db: AsyncSession, course_id: uuid.UUID) -> int:
    result = await db.execute(select(func.count()).select_from(Enrollment).where(Enrollment.course_id == course_id))
    return result.scalar_one()


async def _completed_lesson_ids(db: AsyncSession, user_id: uuid.UUID, course_id: uuid.UUID) -> set[uuid.UUID]:
    result = await db.execute(
        select(LessonCompletion.lesson_id).where(
            LessonCompletion.user_id == user_id, LessonCompletion.course_id == course_id
        )
    )
    return {row for row in result.scalars()}


async def _is_enrolled(db: AsyncSession, user_id: uuid.UUID, course_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Enrollment.id).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
    )
    return result.scalar_one_or_none() is not None


async def _latest_attempts_by_user(db: AsyncSession, course_id: uuid.UUID) -> dict[uuid.UUID, QuizAttempt]:
    result = await db.execute(
        select(QuizAttempt).where(QuizAttempt.course_id == course_id).order_by(QuizAttempt.attempted_at.asc())
    )
    latest: dict[uuid.UUID, QuizAttempt] = {}
    for attempt in result.scalars():
        latest[attempt.user_id] = attempt  # last write per user wins (ascending order)
    return latest


async def _latest_attempt_for(db: AsyncSession, user_id: uuid.UUID, course_id: uuid.UUID) -> QuizAttempt | None:
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user_id, QuizAttempt.course_id == course_id)
        .order_by(QuizAttempt.attempted_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


# ---------------------------------------------------------------- catalog --
async def list_courses(
    db: AsyncSession, *, user: User | None, search: str | None, category: str | None
) -> list[CourseListItem]:
    result = await db.execute(select(Course).options(selectinload(Course.lessons)).order_by(Course.created_at))
    courses = list(result.scalars())

    if category and category != "All":
        courses = [c for c in courses if c.category == category]
    if search:
        q = search.strip().lower()
        courses = [
            c
            for c in courses
            if q in c.title.lower() or q in c.instructor_name.lower() or q in c.category.lower()
        ]

    items: list[CourseListItem] = []
    for course in courses:
        students = await _students_count(db, course.id)
        enrolled = False
        progress_pct = 0
        if user is not None:
            enrolled = await _is_enrolled(db, user.id, course.id)
            if enrolled and course.lessons:
                done = await _completed_lesson_ids(db, user.id, course.id)
                progress_pct = round(100 * len(done) / len(course.lessons))
        items.append(
            CourseListItem(
                id=course.id,
                title=course.title,
                category=course.category,
                level=course.level,
                instructor_name=course.instructor_name,
                rating=course.rating,
                students=students,
                duration_hrs=course.duration_hrs,
                swatch=course.swatch,
                lesson_count=len(course.lessons),
                enrolled=enrolled,
                progress_pct=progress_pct,
            )
        )
    return items


async def list_categories(db: AsyncSession) -> list[str]:
    result = await db.execute(select(Course.category).distinct().order_by(Course.category))
    return ["All", *[row for row in result.scalars()]]


async def get_course_detail(db: AsyncSession, course_id: uuid.UUID, *, user: User | None) -> CourseDetail:
    course = await _get_course_or_404(db, course_id)
    students = await _students_count(db, course.id)

    enrolled = False
    progress_pct = 0
    done_count = 0
    quiz_attempted = False
    quiz_best_score: int | None = None
    completed_ids: set[uuid.UUID] = set()

    if user is not None:
        enrolled = await _is_enrolled(db, user.id, course.id)
        completed_ids = await _completed_lesson_ids(db, user.id, course.id)
        done_count = len(completed_ids)
        if course.lessons:
            progress_pct = round(100 * done_count / len(course.lessons))
        attempt = await _latest_attempt_for(db, user.id, course.id)
        if attempt is not None:
            quiz_attempted = True
            quiz_best_score = attempt.score

    lessons = [
        LessonOut(
            id=l.id,
            title=l.title,
            type=l.type,
            duration=l.duration,
            body=l.body,
            video_url=l.video_url,
            done=l.id in completed_ids,
        )
        for l in course.lessons
    ]

    return CourseDetail(
        id=course.id,
        title=course.title,
        category=course.category,
        level=course.level,
        instructor_name=course.instructor_name,
        rating=course.rating,
        students=students,
        duration_hrs=course.duration_hrs,
        swatch=course.swatch,
        lesson_count=len(course.lessons),
        enrolled=enrolled,
        progress_pct=progress_pct,
        description=course.description,
        lessons=lessons,
        has_quiz=len(course.quiz_questions) > 0,
        quiz_question_count=len(course.quiz_questions),
        quiz_attempted=quiz_attempted,
        quiz_best_score=quiz_best_score,
        done_count=done_count,
    )


async def get_quiz_questions(db: AsyncSession, course_id: uuid.UUID) -> list[QuizQuestionOut]:
    course = await _get_course_or_404(db, course_id)
    return [
        QuizQuestionOut(id=q.id, type=q.type, text=q.text, options=q.options) for q in course.quiz_questions
    ]


# ------------------------------------------------------------- enrollment --
async def enroll(db: AsyncSession, user: User, course_id: uuid.UUID) -> None:
    course = await _get_course_or_404(db, course_id)
    already = await _is_enrolled(db, user.id, course.id)
    if already:
        return
    db.add(Enrollment(user_id=user.id, course_id=course.id))
    await db.flush()


async def complete_lesson(db: AsyncSession, user: User, course_id: uuid.UUID, lesson_id: uuid.UUID) -> None:
    course = await _get_course_or_404(db, course_id)
    if not await _is_enrolled(db, user.id, course.id):
        raise LmsError("not_enrolled", "You are not enrolled in this course.", status_code=403)

    lesson_ids = {l.id for l in course.lessons}
    if lesson_id not in lesson_ids:
        raise LmsError("not_found", "Lesson not found in this course.", status_code=404)

    already_done = await _completed_lesson_ids(db, user.id, course.id)
    if lesson_id in already_done:
        return

    db.add(LessonCompletion(user_id=user.id, course_id=course.id, lesson_id=lesson_id))
    await db.flush()


async def submit_quiz(
    db: AsyncSession, user: User, course_id: uuid.UUID, payload: QuizSubmitRequest
) -> QuizSubmitResponse:
    settings = get_settings()
    course = await _get_course_or_404(db, course_id)
    if not await _is_enrolled(db, user.id, course.id):
        raise LmsError("not_enrolled", "You are not enrolled in this course.", status_code=403)
    if not course.quiz_questions:
        raise LmsError("no_quiz", "This course has no quiz.", status_code=404)

    given_by_question = {a.question_id: a.value for a in payload.answers}
    review: list[QuizReviewItem] = []
    correct_count = 0

    for question in course.quiz_questions:
        given_raw = given_by_question.get(question.id)
        ok = False
        given_label = "Not answered"
        correct_label = ""

        if question.type.value == "mcq":
            options = question.options or []
            correct_label = options[question.answer] if isinstance(question.answer, int) and question.answer < len(options) else ""
            if given_raw is not None:
                try:
                    given_idx = int(given_raw)
                    given_label = options[given_idx] if 0 <= given_idx < len(options) else "Not answered"
                    ok = given_idx == question.answer
                except ValueError:
                    given_label = "Not answered"
        elif question.type.value == "tf":
            correct_label = "True" if question.answer else "False"
            if given_raw is not None and given_raw != "":
                given_bool = given_raw.strip().lower() == "true"
                given_label = "True" if given_bool else "False"
                ok = given_bool == bool(question.answer)
        else:  # short
            correct_label = str(question.answer)
            if given_raw and given_raw.strip():
                given_label = given_raw.strip()
                g = given_label.strip().lower()
                a = str(question.answer).strip().lower()
                ok = bool(g) and (g == a or g in a or a in g)

        if ok:
            correct_count += 1
        review.append(QuizReviewItem(text=question.text, given=given_label, correct=correct_label, ok=ok))

    total = len(course.quiz_questions)
    score = round(100 * correct_count / total) if total else 0
    passed = score >= settings.default_passing_score

    db.add(
        QuizAttempt(
            user_id=user.id,
            course_id=course.id,
            score=score,
            correct_count=correct_count,
            total_count=total,
            passed=passed,
            review=[r.model_dump() for r in review],
        )
    )
    await db.flush()

    return QuizSubmitResponse(score=score, correct_count=correct_count, total_count=total, passed=passed, review=review)


# --------------------------------------------------------------- dashboard --
async def dashboard(db: AsyncSession, user: User) -> tuple[DashboardStats, list[EnrolledCourseOut]]:
    settings = get_settings()
    result = await db.execute(
        select(Enrollment, Course)
        .join(Course, Course.id == Enrollment.course_id)
        .options(selectinload(Course.lessons))
        .where(Enrollment.user_id == user.id)
    )
    rows = result.all()

    enrolled_courses: list[EnrolledCourseOut] = []
    completed = 0
    scores: list[int] = []
    certificates = 0

    for _enrollment, course in rows:
        completed_ids = await _completed_lesson_ids(db, user.id, course.id)
        total = len(course.lessons)
        pct = round(100 * len(completed_ids) / total) if total else 0
        attempt = await _latest_attempt_for(db, user.id, course.id)
        quiz_attempted = attempt is not None
        quiz_score = attempt.score if attempt else None

        is_complete = total > 0 and len(completed_ids) == total
        if is_complete:
            completed += 1
        if quiz_attempted:
            scores.append(quiz_score)

        has_certificate = (
            settings.certificates_enabled and is_complete and quiz_attempted and quiz_score >= settings.default_passing_score
        )
        if has_certificate:
            certificates += 1

        enrolled_courses.append(
            EnrolledCourseOut(
                id=course.id,
                title=course.title,
                swatch=course.swatch,
                progress_pct=pct,
                done_count=len(completed_ids),
                lesson_total=total,
                quiz_attempted=quiz_attempted,
                quiz_score=quiz_score,
                has_certificate=has_certificate,
            )
        )

    avg_score = round(sum(scores) / len(scores)) if scores else 0
    stats = DashboardStats(
        stat_enrolled=len(rows), stat_completed=completed, stat_avg_score=avg_score, stat_certificates=certificates
    )
    return stats, enrolled_courses


# --------------------------------------------------------------- instructor --
async def instructor_list_courses(db: AsyncSession, user: User) -> list[InstructorCourseListItem]:
    result = await db.execute(
        select(Course)
        .options(selectinload(Course.lessons))
        .where(Course.instructor_id == user.id)
        .order_by(Course.created_at)
    )
    courses = list(result.scalars())
    items = []
    for course in courses:
        students = await _students_count(db, course.id)
        completion_rate, avg_quiz_score = await _course_completion_and_quiz(db, course)
        items.append(
            InstructorCourseListItem(
                id=course.id,
                title=course.title,
                students=students,
                completion_rate=completion_rate,
                avg_quiz_score=avg_quiz_score,
                rating=course.rating,
                swatch=course.swatch,
            )
        )
    return items


async def _course_completion_and_quiz(db: AsyncSession, course: Course) -> tuple[int, int]:
    result = await db.execute(select(Enrollment.user_id).where(Enrollment.course_id == course.id))
    student_ids = list(result.scalars())
    total_lessons = len(course.lessons) if course.lessons else 0

    completed_students = 0
    if student_ids and total_lessons:
        for uid in student_ids:
            done = await _completed_lesson_ids(db, uid, course.id)
            if len(done) == total_lessons:
                completed_students += 1
    completion_rate = round(100 * completed_students / len(student_ids)) if student_ids else 0

    latest = await _latest_attempts_by_user(db, course.id)
    avg_quiz_score = round(sum(a.score for a in latest.values()) / len(latest)) if latest else 0

    return completion_rate, avg_quiz_score


async def get_course_for_edit(db: AsyncSession, user: User, course_id: uuid.UUID) -> Course:
    course = await _get_course_or_404(db, course_id)
    if course.instructor_id != user.id:
        raise LmsError("forbidden", "You can only edit your own courses.", status_code=403)
    return course


async def get_quiz_questions_for_edit(db: AsyncSession, user: User, course_id: uuid.UUID) -> list[QuizQuestionInstructorOut]:
    course = await get_course_for_edit(db, user, course_id)
    return [
        QuizQuestionInstructorOut(id=q.id, type=q.type, text=q.text, options=q.options, answer=q.answer)
        for q in course.quiz_questions
    ]


def _apply_course_payload(course: Course, payload: CourseCreate) -> None:
    course.title = payload.title
    course.category = payload.category
    course.level = payload.level
    course.instructor_name = payload.instructor_name
    course.duration_hrs = payload.duration_hrs
    course.rating = payload.rating
    course.swatch = payload.swatch
    course.description = payload.description

    course.lessons.clear()
    for idx, lesson_in in enumerate(payload.lessons):
        course.lessons.append(
            Lesson(
                title=lesson_in.title,
                type=lesson_in.type,
                duration=lesson_in.duration,
                body=lesson_in.body,
                video_url=lesson_in.video_url,
                order_index=idx,
            )
        )

    course.quiz_questions.clear()
    for idx, q_in in enumerate(payload.quiz_questions):
        course.quiz_questions.append(
            QuizQuestion(type=q_in.type, text=q_in.text, options=q_in.options, answer=q_in.answer, order_index=idx)
        )


async def instructor_create_course(db: AsyncSession, user: User, payload: CourseCreate) -> Course:
    course = Course(instructor_id=user.id, instructor_name=payload.instructor_name, title=payload.title, category=payload.category, level=payload.level, duration_hrs=payload.duration_hrs)
    _apply_course_payload(course, payload)
    db.add(course)
    await db.flush()
    return course


async def instructor_update_course(db: AsyncSession, user: User, course_id: uuid.UUID, payload: CourseCreate) -> Course:
    course = await get_course_for_edit(db, user, course_id)
    _apply_course_payload(course, payload)
    await db.flush()
    return course


async def analytics(db: AsyncSession, user: User) -> AnalyticsOut:
    result = await db.execute(select(Course).options(selectinload(Course.lessons)).where(Course.instructor_id == user.id))
    courses = list(result.scalars())

    rows: list[AnalyticsCourseRow] = []
    total_students = 0
    completion_rates = []
    quiz_scores = []

    for course in courses:
        students = await _students_count(db, course.id)
        completion_rate, avg_quiz_score = await _course_completion_and_quiz(db, course)
        total_students += students
        completion_rates.append(completion_rate)
        if avg_quiz_score:
            quiz_scores.append(avg_quiz_score)
        rows.append(
            AnalyticsCourseRow(
                id=course.id, title=course.title, students=students, completion_rate=completion_rate, avg_quiz_score=avg_quiz_score, rating=course.rating
            )
        )

    avg_completion = round(sum(completion_rates) / len(completion_rates)) if completion_rates else 0
    avg_quiz_all = round(sum(quiz_scores) / len(quiz_scores)) if quiz_scores else 0

    return AnalyticsOut(total_students=total_students, avg_completion_rate=avg_completion, avg_quiz_score_all=avg_quiz_all, courses=rows)
