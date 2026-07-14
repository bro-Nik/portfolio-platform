from typing import Any

from pydantic import BaseModel


class RequestLogCreate(BaseModel):
    provider_name: str
    endpoint: str
    method: str
    status_code: int
    response_time: float
    was_successful: bool
    error_message: str
    request_params: dict[str, Any]
    task_id: int


class RequestLogUpdate(BaseModel):
    pass
