from .portfolio import PortfolioResponse
from .wallet import WalletResponse
from app.common.schemas import ApiModel


class OverviewResponse(ApiModel):
    portfolios: list[PortfolioResponse]
    wallets: list[WalletResponse]


OverviewResponse.model_rebuild()
