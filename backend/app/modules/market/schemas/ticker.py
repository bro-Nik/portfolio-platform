from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TickerResponse(BaseModel):
    id: int
    name: str
    symbol: str
    image: str | None = None
    market_cap_rank: int | None = None
    price: float
    market: str
    model_config = ConfigDict(from_attributes=True)


class TickerDetailResponse(TickerResponse):
    is_active: bool
    price_updated_by: str | None = None
    updated_at: datetime | None = None


class TickerSearchResponse(BaseModel):
    data: list[TickerResponse]
    has_more: bool
    total: int


class TickerListResponse(BaseModel):
    data: list[TickerDetailResponse]
    has_more: bool
    total: int


class PricesResponse(BaseModel):
    prices: dict[int, float]


class ImagesResponse(BaseModel):
    images: dict[int, str]


class TickerInfo(BaseModel):
    name: str
    symbol: str
    image: str | None = None
    market: str | None = None


class TickerInfoListResponse(BaseModel):
    info: dict[int, TickerInfo]


class TickerUpdateRequest(BaseModel):
    name: str | None = None
    symbol: str | None = None
    is_active: bool | None = None


class TickerMergeRequest(BaseModel):
    source_id: int
    target_id: int
