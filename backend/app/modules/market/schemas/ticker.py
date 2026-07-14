from pydantic import BaseModel, ConfigDict


class TickerResponse(BaseModel):
    id: str
    name: str
    symbol: str
    image: str | None = None
    market_cap_rank: int | None = None
    price: float
    market: str
    model_config = ConfigDict(from_attributes=True)


class TickerSearchResponse(BaseModel):
    data: list[TickerResponse]
    has_more: bool


class PricesResponse(BaseModel):
    prices: dict[str, float]


class ImagesResponse(BaseModel):
    images: dict[str, str]


class TickerInfoListResponse(BaseModel):
    info: dict[str, dict]
