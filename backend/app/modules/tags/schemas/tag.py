from typing import Literal

from pydantic import BaseModel

from app.common.schemas import ApiModel


TagScope = Literal['portfolio', 'wallet', 'asset']
TagEntityType = Literal['portfolio', 'wallet', 'portfolio_asset', 'wallet_asset']


class TagResponse(ApiModel):
    id: int
    name: str
    color: str | None = None
    scope: TagScope


class TagCreate(ApiModel):
    name: str
    color: str | None = None
    scope: TagScope


class TagUpdate(ApiModel):
    name: str | None = None
    color: str | None = None
