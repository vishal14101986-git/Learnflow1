"""Seeds demo data: 12 default courses (ported from the design project) owned
by one demo instructor account, plus a demo learner account.

Run with: python -m app.seed
"""

import asyncio

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.course import Course, CourseLevel
from app.models.lesson import Lesson, LessonType
from app.models.quiz import QuestionType, QuizQuestion
from app.models.user import User, UserRole, UserStatus
from app.security.passwords import hash_password
from app.seed_data import DEFAULT_COURSES

DEMO_INSTRUCTOR_EMAIL = "instructor@learnflow.dev"
DEMO_LEARNER_EMAIL = "learner@learnflow.dev"
DEMO_PASSWORD = "LearnFlowDemo!2026"


async def _ensure_demo_user(db, *, email: str, name: str, role: UserRole) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is not None:
        return user
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(DEMO_PASSWORD),
        role=role,
        status=UserStatus.active,
    )
    db.add(user)
    await db.flush()
    return user


async def seed() -> None:
    async with SessionLocal() as db:
        instructor = await _ensure_demo_user(db, email=DEMO_INSTRUCTOR_EMAIL, name="Demo Instructor", role=UserRole.instructor)
        await _ensure_demo_user(db, email=DEMO_LEARNER_EMAIL, name="Demo Learner", role=UserRole.learner)

        existing = await db.execute(select(Course.id))
        if existing.first() is not None:
            print("Courses already seeded, skipping.")
            await db.commit()
            return

        for course_data in DEFAULT_COURSES:
            course = Course(
                instructor_id=instructor.id,
                instructor_name=course_data["instructor_name"],
                title=course_data["title"],
                category=course_data["category"],
                level=CourseLevel(course_data["level"]),
                duration_hrs=course_data["duration_hrs"],
                rating=course_data["rating"],
                swatch=course_data["swatch"],
                description=course_data["description"],
            )
            for idx, lesson_data in enumerate(course_data["lessons"]):
                course.lessons.append(
                    Lesson(
                        title=lesson_data["title"],
                        type=LessonType(lesson_data["type"]),
                        duration=lesson_data["duration"],
                        body=lesson_data["body"],
                        order_index=idx,
                    )
                )
            for idx, q_data in enumerate(course_data["quiz"]):
                course.quiz_questions.append(
                    QuizQuestion(
                        type=QuestionType(q_data["type"]),
                        text=q_data["text"],
                        options=q_data.get("options"),
                        answer=q_data["answer"],
                        order_index=idx,
                    )
                )
            db.add(course)

        await db.commit()
        print(f"Seeded {len(DEFAULT_COURSES)} courses.")
        print(f"Demo instructor: {DEMO_INSTRUCTOR_EMAIL} / {DEMO_PASSWORD}")
        print(f"Demo learner:    {DEMO_LEARNER_EMAIL} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
