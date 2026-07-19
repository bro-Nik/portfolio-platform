from pydantic import BaseModel

from .portfolio import PortfolioResponse
from .wallet import WalletResponse


class OverviewResponse(BaseModel):
    portfolios: list[PortfolioResponse]
    wallets: list[WalletResponse]


OverviewResponse.model_rebuild()
