from typing import Literal

from pydantic import BaseModel, ConfigDict


TagScope = Literal['portfolio', 'wallet', 'asset']


class TagResponse(BaseModel):
    id: int
    name: str
    color: str | None = None
    scope: TagScope
    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseModel):
    name: str
    color: str | None = None
    scope: TagScope


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class TagAttachRequest(BaseModel):
    tag_id: int
    entity_type: str
    entity_id: int
