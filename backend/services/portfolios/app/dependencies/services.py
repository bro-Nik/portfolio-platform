from typing import Annotated

from fastapi import Depends

from app.dependencies import DBSession
from app.services import (
    PortfolioAssetService,
    PortfolioService,
    TransactionService,
    WalletAssetService,
    WalletService,
)


def get_portfolio_service(session: DBSession) -> PortfolioService:
    """Зависимость для получения сервиса портфелей."""
    return PortfolioService(session)


def get_portfolio_asset_service(session: DBSession) -> PortfolioAssetService:
    """Зависимость для получения сервиса активов портфелей."""
    return PortfolioAssetService(session)


def get_wallet_service(session: DBSession) -> WalletService:
    """Зависимость для получения сервиса кошельков."""
    return WalletService(session)


def get_wallet_asset_service(session: DBSession) -> WalletAssetService:
    """Зависимость для получения сервиса активов кошельков."""
    return WalletAssetService(session)


def get_transaction_service(session: DBSession) -> TransactionService:
    """Зависимость для получения сервиса транзакций."""
    return TransactionService(session)


PortfolioServiceDep = Annotated[PortfolioService, Depends(get_portfolio_service)]
PortfolioAssetServiceDep = Annotated[PortfolioAssetService, Depends(get_portfolio_asset_service)]
WalletServiceDep = Annotated[WalletService, Depends(get_wallet_service)]
WalletAssetServiceDep = Annotated[WalletAssetService, Depends(get_wallet_asset_service)]
TransactionServiceDep = Annotated[TransactionService, Depends(get_transaction_service)]
