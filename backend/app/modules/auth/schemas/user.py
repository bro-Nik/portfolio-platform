from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field

from app.core import settings

from .session import LoginSessionResponse


class UserRole(str, Enum):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    @property
    def priority(self) -> int:
        return {
            UserRole.USER: 1,
            UserRole.MODERATOR: 2,
            UserRole.ADMIN: 3,
        }.get(self, 1)


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER
    status: str = 'active'


class UserUpdateRequest(BaseModel):
    role: UserRole = UserRole.USER
    status: str = 'active'


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    status: str
    created_at: datetime | None = None
    last_active_at: datetime | None = None
    total_active_time: int = Field(0, description='Total time on site in seconds')
    login_sessions: list[LoginSessionResponse] | None = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def online(self) -> bool:
        if not self.last_active_at:
            return False
        time_diff = datetime.now(UTC) - self.last_active_at
        return time_diff.total_seconds() < settings.jwt_access_token_expire_minutes * 60


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password_hash: str
    role: UserRole = UserRole.USER
    status: str = 'active'


class UserUpdate(BaseModel):
    role: UserRole = UserRole.USER
    status: str = 'active'
