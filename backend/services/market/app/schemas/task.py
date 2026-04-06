from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class TaskBase(BaseModel):
    """Базовые поля."""

    name: str
    provider_id: int
    task_type: str
    schedule: str  # cron выражение, например "0 * * * *" (каждый час)
    is_active: bool = True
    parameters: dict[str, Any] = {}


class TaskCreateRequest(TaskBase):
    """Создание новой API задачу."""


class TaskUpdateRequest(TaskBase):
    """Обновление API задачи."""


class TaskCreate(TaskBase):
    """Создание API задачи в БД."""


class TaskUpdate(TaskBase):
    """Обновление API задачи в БД."""


class TaskResponse(BaseModel):
    """Ответ с данными задачи."""

    id: int
    name: str
    description: str | None
    status: str | None
    task_type: str
    schedule: str
    is_active: bool
    parameters: dict[str, Any]
    last_run: datetime | None = None
    next_run: datetime | None = None
    provider: 'ProviderResponse'

    model_config = ConfigDict(from_attributes=True)
