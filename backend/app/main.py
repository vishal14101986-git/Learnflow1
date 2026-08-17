from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes.auth import router as auth_router
from app.api.routes.courses import router as courses_router
from app.api.routes.instructor import router as instructor_router
from app.core.config import get_settings
from app.security.passwords import PasswordPolicyError
from app.security.rate_limit import limiter

settings = get_settings()

app = FastAPI(title="LearnFlow API", version="0.1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(PasswordPolicyError)
async def password_policy_handler(request: Request, exc: PasswordPolicyError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": exc.message})


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(courses_router)
app.include_router(instructor_router)
