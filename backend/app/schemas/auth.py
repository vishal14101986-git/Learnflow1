import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole, UserStatus


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=1, max_length=4096)
    confirm_password: str = Field(min_length=1, max_length=4096)
    role: UserRole = UserRole.learner

    @field_validator("role")
    @classmethod
    def only_learner_or_instructor(cls, v: UserRole) -> UserRole:
        if v == UserRole.administrator:
            raise ValueError("Cannot self-register as administrator.")
        return v


class GenericMessage(BaseModel):
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=4096)


class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    role: UserRole
    status: UserStatus

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=1, max_length=4096)
    confirm_password: str = Field(min_length=1, max_length=4096)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=4096)
    new_password: str = Field(min_length=1, max_length=4096)
    confirm_password: str = Field(min_length=1, max_length=4096)
