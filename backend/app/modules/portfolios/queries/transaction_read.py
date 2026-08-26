from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.market.services.ticker import TickerService
from app.modules.portfolios.models import Transaction
from app.modules.portfolios.services.portfolio_asset import PortfolioAssetService
from app.modules.portfolios.services.wallet_asset import WalletAssetService


class TransactionReadQuery:
    def __init__(self, session: AsyncSession, ctx: Context, ticker_service: TickerService) -> None:
        self.session = session
        self.ctx = ctx
        self.ticker_service = ticker_service
        self.portfolio_asset_service = PortfolioAssetService(ctx, session)
        self.wallet_asset_service = WalletAssetService(ctx, session)

    async def _enrich(self, transactions: list[Transaction]) -> None:
        if not transactions:
            return
        ticker_ids = set()
        for t in transactions:
            if t.ticker_id:
                ticker_ids.add(t.ticker_id)
            if t.ticker2_id:
                ticker_ids.add(t.ticker2_id)
        info_map = await self.ticker_service.get_info(list(ticker_ids))
        for t in transactions:
            tk = info_map.get(t.ticker_id)
            if tk:
                t.ticker_symbol = tk.symbol
            tk2 = info_map.get(t.ticker2_id)
            if tk2:
                t.ticker2_symbol = tk2.symbol

    async def get_portfolio_asset_transactions(self, asset_id: int) -> list[Transaction]:
        transactions = await self.portfolio_asset_service.get_transactions(asset_id)
        await self._enrich(transactions)
        return transactions

    async def get_wallet_asset_transactions(self, asset_id: int) -> list[Transaction]:
        transactions = await self.wallet_asset_service.get_transactions(asset_id)
        await self._enrich(transactions)
        return transactions
