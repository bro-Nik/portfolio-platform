from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exporting import fetch_all, model_rows
from app.modules.auth.protocols import ExportAccumulator, UserDataCollector
from app.modules.portfolios.models import Portfolio, PortfolioAsset, Transaction, Wallet, WalletAsset


class PortfolioDataCollector(UserDataCollector):
    """Разделы портфелей/кошельков/транзакций + сбор ticker_ids для market."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def collect(self, user_id: int, acc: ExportAccumulator) -> None:
        portfolios = await fetch_all(self._session, Portfolio, Portfolio.user_id == user_id)
        wallets = await fetch_all(self._session, Wallet, Wallet.user_id == user_id)
        transactions = await fetch_all(self._session, Transaction, Transaction.user_id == user_id)
        portfolio_assets = await fetch_all(self._session, PortfolioAsset, PortfolioAsset.user_id == user_id)
        wallet_assets = await fetch_all(self._session, WalletAsset, WalletAsset.user_id == user_id)
        acc.sections['portfolios'] = model_rows(portfolios)
        acc.sections['portfolio_assets'] = model_rows(portfolio_assets)
        acc.sections['wallets'] = model_rows(wallets)
        acc.sections['wallet_assets'] = model_rows(wallet_assets)
        acc.sections['transactions'] = model_rows(transactions)
        acc.ticker_ids |= {
            *[a.ticker_id for a in portfolio_assets],
            *[a.ticker_id for a in wallet_assets],
            *[t.ticker_id for t in transactions if t.ticker_id],
            *[t.ticker2_id for t in transactions if t.ticker2_id],
        }
