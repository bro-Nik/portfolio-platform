from datetime import datetime
from decimal import Decimal

from .portfolio import PortfolioAssetResponse
from .wallet import WalletAssetResponse
from app.common.schemas import ApiModel


class TransactionBase(ApiModel):
    date: datetime
    ticker_id: int
    ticker2_id: int | None = None
    quantity: Decimal
    quantity2: Decimal | None = None
    price: Decimal | None = None
    price_usd: Decimal | None = None
    type: str
    comment: str | None = None
    wallet_id: int | None = None
    wallet2_id: int | None = None
    portfolio_id: int | None = None
    portfolio2_id: int | None = None
    order: bool | None = None


class TransactionResponse(TransactionBase):
    id: int
    ticker_symbol: str | None = None
    ticker2_symbol: str | None = None


class TransactionCreateRequest(TransactionBase):
    pass


class TransactionUpdateRequest(ApiModel):
    date: datetime | None = None
    ticker_id: int | None = None
    ticker2_id: int | None = None
    quantity: Decimal | None = None
    quantity2: Decimal | None = None
    price: Decimal | None = None
    price_usd: Decimal | None = None
    type: str | None = None
    comment: str | None = None
    wallet_id: int | None = None
    wallet2_id: int | None = None
    portfolio_id: int | None = None
    portfolio2_id: int | None = None
    order: bool | None = None


class TransactionCreate(TransactionBase):
    user_id: int


class TransactionUpdate(TransactionBase):
    pass


class TransactionResponseWithAssets(ApiModel):
    success: bool = True
    message: str | None = None
    transaction: TransactionResponse | None = None
    portfolio_assets: list[PortfolioAssetResponse] | None = None
    wallet_assets: list[WalletAssetResponse] | None = None


TransactionResponseWithAssets.model_rebuild()
