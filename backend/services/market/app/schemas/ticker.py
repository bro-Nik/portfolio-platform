from pydantic import BaseModel, ConfigDict


class TickerResponse(BaseModel):
    """Модель ответа для тикера."""

    id: str
    name: str
    symbol: str
    image: str | None = None
    market_cap_rank: int | None = None
    price: float
    market: str

    model_config = ConfigDict(from_attributes=True)


class TickerSearchResponse(BaseModel):
    """Модель ответа для поиска тикеров."""

    data: list[TickerResponse]
    has_more: bool


class PricesResponse(BaseModel):
    """Модель ответа для цен активов."""

    prices: dict[str, float]


class ImagesResponse(BaseModel):
    """Модель ответа для картинок активов."""

    images: dict[str, str]


class TickerInfoListResponse(BaseModel):
    """Модель ответа для информации о активове."""

    info: dict[str, dict]
