from pydantic import BaseModel

from app.common.schemas import ApiModel

from app.common.utils.decimal import CleanDecimal
from app.modules.tags.schemas import TagResponse


class PortfolioBase(ApiModel):
    name: str
    comment: str | None = None


class PortfolioCreateRequest(PortfolioBase):
    market: str


class PortfolioUpdateRequest(PortfolioBase):
    market: str | None = None


class PortfolioArchiveRequest(ApiModel):
    is_archived: bool


class PortfolioAssetArchiveRequest(ApiModel):
    is_archived: bool


class PortfolioCreate(PortfolioBase):
    user_id: int
    market: str


class PortfolioUpdate(PortfolioBase):
    market: str | None = None


class PortfolioAssetBase(ApiModel):
    portfolio_id: int
    ticker_id: int


class PortfolioAssetCreateRequest(ApiModel):
    ticker_id: int
    portfolio_id: int


class PortfolioAssetCreate(PortfolioAssetBase):
    user_id: int


class PortfolioAssetUpdate(PortfolioAssetBase):
    pass


class PortfolioAssetResponse(PortfolioAssetBase):
    id: int
    quantity: CleanDecimal
    amount: CleanDecimal
    realized_profit: CleanDecimal
    total_invested: CleanDecimal
    buy_orders: CleanDecimal
    sell_orders: CleanDecimal
    is_archived: bool
    has_transactions: bool = False
    tags: list[TagResponse] = []
    name: str | None = None
    symbol: str | None = None
    image: str | None = None
    market: str | None = None


class PortfolioResponse(PortfolioBase):
    id: int
    market: str
    is_archived: bool
    has_transactions: bool = False
    assets: list[PortfolioAssetResponse] = []
    tags: list[TagResponse] = []


class PortfolioListResponse(ApiModel):
    portfolios: list[PortfolioResponse]


PortfolioResponse.model_rebuild()
PortfolioListResponse.model_rebuild()
