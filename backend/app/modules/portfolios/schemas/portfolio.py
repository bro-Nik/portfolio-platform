from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from .tag import TagResponse


class PortfolioBase(BaseModel):
    name: str
    comment: str | None = None


class PortfolioCreateRequest(PortfolioBase):
    market: str


class PortfolioUpdateRequest(PortfolioBase):
    pass


class PortfolioCreate(PortfolioBase):
    user_id: int
    market: str


class PortfolioUpdate(PortfolioBase):
    pass


class PortfolioAssetBase(BaseModel):
    portfolio_id: int
    ticker_id: int


class PortfolioAssetCreateRequest(BaseModel):
    ticker_id: int
    portfolio_id: int


class PortfolioAssetCreate(PortfolioAssetBase):
    user_id: int


class PortfolioAssetUpdate(PortfolioAssetBase):
    pass


class PortfolioAssetResponse(PortfolioAssetBase):
    id: int
    quantity: Decimal
    amount: Decimal
    realized_profit: Decimal
    total_invested: Decimal
    buy_orders: Decimal
    is_archived: bool
    has_transactions: bool = False
    tags: list[TagResponse] = []
    name: str | None = None
    symbol: str | None = None
    image: str | None = None
    model_config = ConfigDict(from_attributes=True)


class PortfolioResponse(PortfolioBase):
    id: int
    market: str
    is_archived: bool
    has_transactions: bool = False
    assets: list[PortfolioAssetResponse] = []
    tags: list[TagResponse] = []
    model_config = ConfigDict(from_attributes=True)


class PortfolioListResponse(BaseModel):
    portfolios: list[PortfolioResponse]


class PortfolioDeleteResponse(BaseModel):
    portfolio_id: int


class PortfolioAssetCreateResponse(BaseModel):
    pass


PortfolioResponse.model_rebuild()
PortfolioListResponse.model_rebuild()
