from datetime import datetime
from decimal import Decimal
from typing import Literal

from app.common.schemas import ApiModel
from app.common.utils.decimal import CleanDecimal

AlertDirection = Literal['above', 'below']


class PriceAlertResponse(ApiModel):
    id: int
    watchlist_item_id: int
    direction: AlertDirection
    target_price_usd: CleanDecimal
    currency_symbol: str
    is_active: bool
    is_archived: bool
    triggered_at: datetime | None = None
    triggered_price: float | None = None
    comment: str | None = None
    created_at: datetime


class PriceAlertCreate(ApiModel):
    direction: AlertDirection | None = None
    target_price_usd: Decimal
    currency_symbol: str = 'USD'
    comment: str | None = None


class PriceAlertUpdate(ApiModel):
    direction: AlertDirection | None = None
    target_price_usd: Decimal | None = None
    currency_symbol: str | None = None
    comment: str | None = None
    is_active: bool | None = None


class WatchlistItemResponse(ApiModel):
    id: int
    ticker_id: int
    comment: str | None = None
    created_at: datetime
    is_archived: bool
    alerts: list[PriceAlertResponse] = []
    name: str | None = None
    symbol: str | None = None
    image: str | None = None
    market: str | None = None
    price: float | None = None


class WatchlistItemCreate(ApiModel):
    ticker_id: int
    comment: str | None = None


class WatchlistItemUpdate(ApiModel):
    comment: str | None = None


class WatchlistItemArchiveRequest(ApiModel):
    is_archived: bool


class PriceAlertArchiveRequest(ApiModel):
    is_archived: bool


class WatchlistListResponse(ApiModel):
    items: list[WatchlistItemResponse]


class TriggeredAlertResponse(PriceAlertResponse):
    """Сработавший алерт с контекстом тикера — для бейджа и тостов без второго запроса."""

    ticker_id: int | None = None
    ticker_symbol: str | None = None
    ticker_name: str | None = None
    current_price: float | None = None


class TriggeredAlertListResponse(ApiModel):
    alerts: list[TriggeredAlertResponse]


WatchlistItemResponse.model_rebuild()
