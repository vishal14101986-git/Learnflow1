import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.course import AnalyticsOut, CourseCreate, CourseDetail, InstructorCourseListItem, QuizQuestionInstructorOut
from app.services import lms_service
from app.services.lms_service import LmsError

router = APIRouter(prefix="/instructor", tags=["instructor"])

require_instructor = require_role("instructor")


def _raise(exc: LmsError):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/courses", response_model=list[InstructorCourseListItem])
async def my_courses(db: AsyncSession = Depends(get_db), user: User = Depends(require_instructor)) -> list[InstructorCourseListItem]:
    return await lms_service.instructor_list_courses(db, user)


@router.get("/courses/{course_id}", response_model=CourseDetail)
async def get_my_course(
    course_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_instructor)
) -> CourseDetail:
    try:
        course = await lms_service.get_course_for_edit(db, user, course_id)
    except LmsError as exc:
        _raise(exc)
    return await lms_service.get_course_detail(db, course.id, user=user)


@router.get("/courses/{course_id}/quiz", response_model=list[QuizQuestionInstructorOut])
async def get_my_course_quiz(
    course_id: uuid.UUID, db: AsyncSession = Depends(get_db), user: User = Depends(require_instructor)
) -> list[QuizQuestionInstructorOut]:
    try:
        return await lms_service.get_quiz_questions_for_edit(db, user, course_id)
    except LmsError as exc:
        _raise(exc)


@router.post("/courses", response_model=CourseDetail, status_code=201)
async def create_course(
    payload: CourseCreate, db: AsyncSession = Depends(get_db), user: User = Depends(require_instructor)
) -> CourseDetail:
    course = await lms_service.instructor_create_course(db, user, payload)
    await db.commit()
    return await lms_service.get_course_detail(db, course.id, user=user)


@router.put("/courses/{course_id}", response_model=CourseDetail)
async def update_course(
    course_id: uuid.UUID,
    payload: CourseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_instructor),
) -> CourseDetail:
    try:
        course = await lms_service.instructor_update_course(db, user, course_id, payload)
    except LmsError as exc:
        _raise(exc)
    await db.commit()
    return await lms_service.get_course_detail(db, course.id, user=user)


@router.get("/analytics", response_model=AnalyticsOut)
async def get_analytics(db: AsyncSession = Depends(get_db), user: User = Depends(require_instructor)) -> AnalyticsOut:
    return await lms_service.analytics(db, user)
