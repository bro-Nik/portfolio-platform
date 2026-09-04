from datetime import datetime

from pydantic import BaseModel

from app.common.schemas import ApiModel


class TickerResponse(ApiModel):
    id: int
    name: str
    symbol: str
    image: str | None = None
    market_cap_rank: int | None = None
    price: float
    market: str


class TickerDetailResponse(TickerResponse):
    is_active: bool
    price_updated_by: str | None = None
    updated_at: datetime | None = None


class TickerSearchResponse(ApiModel):
    data: list[TickerResponse]
    has_more: bool
    total: int


class TickerListResponse(ApiModel):
    data: list[TickerDetailResponse]
    has_more: bool
    total: int


class PricesResponse(ApiModel):
    prices: dict[int, float]


class ImagesResponse(ApiModel):
    images: dict[int, str]


class TickerInfo(ApiModel):
    name: str
    symbol: str
    image: str | None = None
    market: str | None = None


class TickerInfoListResponse(ApiModel):
    info: dict[int, TickerInfo]


class TickerUpdateRequest(ApiModel):
    name: str | None = None
    symbol: str | None = None
    is_active: bool | None = None


class TickerMergeRequest(ApiModel):
    source_id: int
    target_id: int
