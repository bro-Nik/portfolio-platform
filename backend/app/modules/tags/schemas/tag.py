from typing import Literal

from pydantic import BaseModel, ConfigDict


TagScope = Literal['portfolio', 'wallet', 'asset']
TagEntityType = Literal['portfolio', 'wallet', 'portfolio_asset', 'wallet_asset']


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
