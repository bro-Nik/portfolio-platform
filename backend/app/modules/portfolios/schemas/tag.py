from pydantic import BaseModel, ConfigDict


class TagResponse(BaseModel):
    id: int
    name: str
    color: str | None = None
    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseModel):
    name: str
    color: str | None = None


class TagUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


class TagAttachRequest(BaseModel):
    tag_id: int
    entity_type: str
    entity_id: int
