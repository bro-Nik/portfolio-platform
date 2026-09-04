from datetime import UTC, datetime

from pydantic import BaseModel, EmailStr, Field, computed_field

from app.common.schemas import ApiModel, UserRole
from app.core import settings

from .session import LoginSessionResponse


class UserCreateRequest(ApiModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER
    status: str = 'active'


class UserUpdateRequest(ApiModel):
    email: EmailStr | None = None
    password: str | None = None
    role: UserRole | None = None
    status: str | None = None


class UserResponse(ApiModel):
    id: int
    email: EmailStr
    role: UserRole
    status: str
    is_verified: bool = False
    created_at: datetime | None = None
    last_active_at: datetime | None = None
    total_active_time: int = Field(0, description='Total time on site in seconds')
    login_sessions: list[LoginSessionResponse] | None = None

    @computed_field
    @property
    def online(self) -> bool:
        if not self.last_active_at:
            return False
        time_diff = datetime.now(UTC) - self.last_active_at
        return time_diff.total_seconds() < settings.jwt_access_token_expire_minutes * 60


class PasswordChangeRequest(ApiModel):
    current_password: str
    new_password: str


class EmailChangeRequest(ApiModel):
    current_password: str
    new_email: EmailStr


class UserLogin(ApiModel):
    email: EmailStr
    password: str


class UserRegister(ApiModel):
    email: EmailStr
    password: str


class RegisterResponse(ApiModel):
    message: str


class ResendVerificationRequest(ApiModel):
    email: EmailStr | None = None
    password: str | None = None


class DeleteAccountRequest(ApiModel):
    current_password: str


class ForgotPasswordRequest(ApiModel):
    email: EmailStr


class ResetPasswordRequest(ApiModel):
    token: str
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    role: UserRole = UserRole.USER
    status: str = 'active'
    is_verified: bool = False
