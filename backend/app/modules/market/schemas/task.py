from datetime import datetime
from typing import Any


from app.common.schemas import ApiModel

class TaskBase(ApiModel):
    name: str
    provider_name: str
    task_type: str
    schedule: str
    is_active: bool = True
    parameters: dict[str, Any] = {}
    next_run: datetime | None = None


class TaskCreateRequest(TaskBase):
    pass


class TaskUpdateRequest(TaskBase):
    pass


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskResponse(ApiModel):
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
