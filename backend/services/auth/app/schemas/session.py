from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoginSessionCreate(BaseModel):
    """Создание сессии входа в БД."""

    user_id: int
    refresh_token_id: int
    ip_address: str | None = None
    user_agent: str | None = None
    device_type: str | None = None
    browser: str | None = None
    os: str | None = None


class LoginSessionUpdate(BaseModel):
    """Обновление сессии входа в БД."""

    ip_address: str | None = None
    last_activity_at: datetime | None = None


class LoginSessionResponse(BaseModel):
    """Ответ с данными сессии."""

    id: int
    ip_address: str | None = None
    device_type: str | None = None
    browser: str | None = None
    os: str | None = None
    platform: str | None = None
    login_at: datetime
    last_activity_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
