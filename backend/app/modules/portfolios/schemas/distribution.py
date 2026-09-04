from decimal import Decimal

from pydantic import BaseModel

from app.common.schemas import ApiModel


class PortfolioAssetDistributionItem(ApiModel):
    portfolio_id: int
    portfolio_name: str
    quantity: Decimal
    amount: Decimal
    percentage_of_total: float


class PortfolioAssetDistributionResponse(ApiModel):
    total_quantity_all_portfolios: Decimal
    total_amount_all_portfolios: Decimal
    portfolios: list[PortfolioAssetDistributionItem]


class WalletAssetDistributionItem(ApiModel):
    wallet_id: int
    wallet_name: str
    quantity: Decimal
    percentage_of_total: float


class WalletAssetDistributionResponse(ApiModel):
    total_quantity_all_wallets: Decimal
    wallets: list[WalletAssetDistributionItem]
