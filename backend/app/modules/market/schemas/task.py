from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

class TaskBase(BaseModel):
    name: str
    provider_name: str
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
    provider_name: str
    schedule: str
    is_active: bool
    parameters: dict[str, Any]
    last_run: datetime | None = None
    next_run: datetime | None = None
    model_config = ConfigDict(from_attributes=True)
