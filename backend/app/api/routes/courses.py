import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.course import CourseDetail, CourseListItem, DashboardOut, QuizQuestionOut, QuizSubmitRequest, QuizSubmitResponse
from app.schemas.auth import GenericMessage
from app.services import lms_service
from app.services.lms_service import LmsError

router = APIRouter(tags=["courses"])


def _raise(exc: LmsError):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/courses", response_model=list[CourseListItem])
async def list_courses(
    q: str | None = None,
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[CourseListItem]:
    return await lms_service.list_courses(db, user=user, search=q, category=category)


@router.get("/courses/categories", response_model=list[str])
async def list_categories(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)) -> list[str]:
    return await lms_service.list_categories(db)


@router.get("/courses/{course_id}", response_model=CourseDetail)
async def get_course(
    course_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
) -> CourseDetail:
    try:
        return await lms_service.get_course_detail(db, course_id, user=user)
    except LmsError as exc:
        _raise(exc)


@router.get("/courses/{course_id}/quiz", response_model=list[QuizQuestionOut])
async def get_quiz(
    course_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
) -> list[QuizQuestionOut]:
    try:
        return await lms_service.get_quiz_questions(db, course_id)
    except LmsError as exc:
        _raise(exc)


@router.post("/courses/{course_id}/enroll", response_model=GenericMessage)
async def enroll(
    course_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
) -> GenericMessage:
    try:
        await lms_service.enroll(db, user, course_id)
    except LmsError as exc:
        _raise(exc)
    await db.commit()
    return GenericMessage(message="Enrolled.")


@router.post("/courses/{course_id}/lessons/{lesson_id}/complete", response_model=GenericMessage)
async def complete_lesson(
    course_id: uuid.UUID,
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> GenericMessage:
    try:
        await lms_service.complete_lesson(db, user, course_id, lesson_id)
    except LmsError as exc:
        _raise(exc)
    await db.commit()
    return GenericMessage(message="Lesson completed.")


@router.post("/courses/{course_id}/quiz/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    course_id: uuid.UUID,
    payload: QuizSubmitRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> QuizSubmitResponse:
    try:
        result = await lms_service.submit_quiz(db, user, course_id, payload)
    except LmsError as exc:
        _raise(exc)
    await db.commit()
    return result


@router.get("/me/dashboard", response_model=DashboardOut)
async def get_dashboard(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
) -> DashboardOut:
    stats, enrolled = await lms_service.dashboard(db, user)
    return DashboardOut(stats=stats, enrolled_courses=enrolled)
