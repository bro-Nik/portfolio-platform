from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field

from app.core import settings
from app.schemas.session import LoginSessionResponse

from . import UserRole


class UserCreateRequest(BaseModel):
    """Создание нового пользователя."""

    email: EmailStr
    password: str
    role: UserRole = UserRole.USER
    status: str = 'active'


class UserUpdateRequest(BaseModel):
    """Обновление данных пользователя."""

    role: UserRole = UserRole.USER
    status: str = 'active'


class UserResponse(BaseModel):
    """Ответ с данными пользователя."""

    id: int
    email: EmailStr
    role: UserRole
    status: str
    created_at: datetime | None = None
    last_active_at: datetime| None = None
    total_active_time: int = Field(0, description='Общее время на сайте в секундах')
    login_sessions: list[LoginSessionResponse] | None = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def online(self) -> bool:
        """Определяет, находится ли пользователь онлайн."""
        if not self.last_active_at:
            return False

        time_diff = datetime.now(UTC) - self.last_active_at
        return time_diff.total_seconds() < settings.jwt_access_token_expire_minutes * 60


class UserLogin(BaseModel):
    """Вход пользователя."""

    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """Регистрация пользователя."""

    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """Создание пользователя в БД."""

    email: EmailStr
    password_hash: str
    role: UserRole = UserRole.USER
    status: str = 'active'


class UserUpdate(BaseModel):
    """Обновление пользователя в БД."""

    role: UserRole = UserRole.USER
    status: str = 'active'
