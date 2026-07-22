from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ProviderBase(BaseModel):
    api_key: str | None = None
    supported_markets: list[str] | None = None
    requests_per_minute: int | None = None
    requests_per_hour: int | None = None
    requests_per_day: int | None = None
    requests_per_month: int | None = None
    retry_delay: int = 60
    timeout: int = 30
    is_active: bool = True


class ProviderCreateRequest(ProviderBase):
    name: str


class ProviderUpdateRequest(ProviderBase):
    pass


class ProviderCreate(ProviderBase):
    name: str


class ProviderUpdate(ProviderBase):
    pass


class ProviderResponse(ProviderBase):
    id: int | None = None
    name: str
    has_config: bool = False
    minute_counter: int | None = None
    hour_counter: int | None = None
    day_counter: int | None = None
    month_counter: int | None = None
    model_config = ConfigDict(from_attributes=True)


class ProviderStats(BaseModel):
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
    utilization_percent: dict[str, float]


class ProviderLog(BaseModel):
    id: int
    provider_name: str | None = None
    endpoint: str
    method: str
    status_code: int | None
    response_time: float | None
    was_successful: bool
    error_message: str | None
    request_params: dict[str, Any] | None
    task_id: int | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
