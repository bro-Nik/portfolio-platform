from dishka import FromDishka

from .di import PortfoliosProvider
from app.common.dependencies import require_user
from app.modules.portfolios.services.portfolio import PortfolioService
from app.modules.portfolios.services.portfolio_asset import PortfolioAssetService
from app.modules.portfolios.services.transaction import TransactionService
from app.modules.portfolios.services.wallet import WalletService
from app.modules.portfolios.services.wallet_asset import WalletAssetService
from app.queries.overview_read import OverviewReadQuery
from app.queries.portfolio_read import PortfolioReadQuery
from app.queries.transaction_read import TransactionReadQuery
from app.queries.wallet_read import WalletReadQuery

PortfolioServiceDep = FromDishka[PortfolioService]
PortfolioAssetServiceDep = FromDishka[PortfolioAssetService]
WalletServiceDep = FromDishka[WalletService]
WalletAssetServiceDep = FromDishka[WalletAssetService]
TransactionServiceDep = FromDishka[TransactionService]
PortfolioReadQueryDep = FromDishka[PortfolioReadQuery]
WalletReadQueryDep = FromDishka[WalletReadQuery]
TransactionReadQueryDep = FromDishka[TransactionReadQuery]
OverviewReadQueryDep = FromDishka[OverviewReadQuery]

__all__ = [
    'OverviewReadQueryDep',
    'PortfolioAssetServiceDep',
    'PortfolioReadQueryDep',
    'PortfolioServiceDep',
    'PortfoliosProvider',
    'TransactionReadQueryDep',
    'TransactionServiceDep',
    'WalletAssetServiceDep',
    'WalletReadQueryDep',
    'WalletServiceDep',
    'require_user',
]
