from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProviderBase(BaseModel):
    """Базовые поля."""

    api_key: str | None = None
    requests_per_minute: int | None = None
    requests_per_hour: int | None = None
    requests_per_day: int | None = None
    requests_per_month: int | None = None
    retry_delay: int = 60
    timeout: int = 30
    is_active: bool = True


class ProviderCreateRequest(ProviderBase):
    """Создание нового API провайдера."""

    name: str


class ProviderUpdateRequest(ProviderBase):
    """Обновление API провайдера."""


class ProviderCreate(ProviderBase):
    """Создание API провайдера в БД."""

    name: str


class ProviderUpdate(ProviderBase):
    """Обновление API провайдера в БД."""


class ProviderResponse(ProviderBase):
    """Ответ с данными API провайдера."""

    id: int
    name: str

    # Текущие счетчики
    minute_counter: int
    hour_counter: int
    day_counter: int
    month_counter: int

    # Время последнего сброса
    last_minute_reset: datetime
    last_hour_reset: datetime
    last_day_reset: datetime
    last_month_reset: datetime

    model_config = ConfigDict(from_attributes=True)


class ProviderStats(BaseModel):
    """Ответ со статистикой API провайдера."""

    provider_name: str
    requests_today: int
    successful_today: int
    failed_today: int
    avg_response_time: float | None
    minute_counter: int
    minute_limit: int
    hour_counter: int
    hour_limit: int
    day_counter: int
    day_limit: int
    month_counter: int
    month_limit: int
    pending_in_queue: int
    utilization_percent: dict[str, float]
