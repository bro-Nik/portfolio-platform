from typing import Any

from pydantic import BaseModel


class RequestLogBase(BaseModel):
    """Базовые поля."""

    provider_name: str
    endpoint: str
    method: str
    status_code: int
    response_time: float
    was_successful: bool
    error_message: str
    request_params: dict[str, Any]
    task_id: int


class RequestLogCreate(RequestLogBase):
    """Создание лога API запроса в БД."""


class RequestLogUpdate(RequestLogBase):
    """Обновление лога API запроса в БД."""
