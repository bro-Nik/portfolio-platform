from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.market.services.ticker import TickerService
from app.modules.portfolios.models import Wallet
from app.modules.portfolios.queries.enrichment import add_has_transactions, enrich_assets_with_ticker_info
from app.modules.portfolios.repositories import TransactionRepository
from app.modules.portfolios.services.wallet import WalletService
from app.modules.tags.repositories import TaggableRepository


class WalletReadQuery:
    def __init__(self, session: AsyncSession, ctx: Context, ticker_service: TickerService) -> None:
        self.session = session
        self.ctx = ctx
        self.ticker_service = ticker_service
        self.taggable_repo = TaggableRepository(session)
        self.service = WalletService(session, ctx, taggable_repo=self.taggable_repo)
        self.transaction_repo = TransactionRepository(session)

    async def enrich(self, wallets: list[Wallet]) -> None:
        await enrich_assets_with_ticker_info(
            [a for w in wallets for a in w.assets],
            self.ticker_service,
        )

    async def add_has_transactions(self, wallets: list[Wallet]) -> None:
        await add_has_transactions(
            wallets,
            [a for w in wallets for a in w.assets],
            parents_with_transactions=self.transaction_repo.wallets_with_transactions,
            parent_tickers_with_transactions=self.transaction_repo.wallets_tickers_with_transactions,
        )

    async def get_with_assets(self, id: int) -> Wallet:
        wallet = await self.service.get_with_assets(id)
        await self.enrich([wallet])
        await self.add_has_transactions([wallet])
        return wallet

    async def get_all_with_assets(self) -> list[Wallet]:
        wallets = await self.service.get_all_with_assets()
        await self.enrich(wallets)
        await self.add_has_transactions(wallets)
        return wallets
