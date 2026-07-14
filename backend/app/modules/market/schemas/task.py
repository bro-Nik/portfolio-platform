from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from .provider import ProviderResponse


class TaskBase(BaseModel):
    name: str
    provider_id: int
    task_type: str
    schedule: str
    is_active: bool = True
    parameters: dict[str, Any] = {}


class TaskCreateRequest(TaskBase):
    pass


class TaskUpdateRequest(TaskBase):
    pass


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskResponse(BaseModel):
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
    provider: ProviderResponse
    model_config = ConfigDict(from_attributes=True)
