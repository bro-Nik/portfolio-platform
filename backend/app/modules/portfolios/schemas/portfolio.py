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
    ticker_id: str


class PortfolioAssetCreateRequest(BaseModel):
    ticker_id: str
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
    tags: list[TagResponse] = []
    model_config = ConfigDict(from_attributes=True)


class PortfolioResponse(PortfolioBase):
    id: int
    market: str
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
