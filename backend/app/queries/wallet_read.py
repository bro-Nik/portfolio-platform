from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.market.repositories.ticker import TickerRepository
from app.modules.portfolios.models import Wallet
from app.modules.portfolios.repositories import TransactionRepository
from app.modules.portfolios.services.wallet import WalletService
from app.modules.tags.repositories import TaggableRepository

IMAGES_URL = '/market/static/images/tickers'


class WalletReadQuery:
    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.session = session
        self.ctx = ctx
        self.service = WalletService(session, ctx, taggable_repo=TaggableRepository(session))
        self.ticker_repo = TickerRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def _enrich(self, wallets: list[Wallet]) -> None:
        all_assets = [a for w in wallets for a in w.assets]
        if not all_assets:
            return
        ticker_ids = list(set(a.ticker_id for a in all_assets))
        tickers_list = await self.ticker_repo.get_all_by_ids(ticker_ids)
        ticker_map = {t.id: t for t in tickers_list}
        for asset in all_assets:
            t = ticker_map.get(asset.ticker_id)
            if t:
                asset.name = t.name
                asset.symbol = t.symbol
                asset.image = f'{IMAGES_URL}/{t.market}/24/{t.image}' if t.image else None

    async def _add_has_transactions(self, wallets: list[Wallet]) -> None:
        wallet_ids = [w.id for w in wallets]
        wallet_txn_ids = await self.transaction_repo.wallets_with_transactions(wallet_ids)
        for w in wallets:
            w.has_transactions = w.id in wallet_txn_ids

        all_assets = [a for w in wallets for a in w.assets]
        wallet_per_asset = {a.id: w.id for w in wallets for a in w.assets}
        assets_by_wallet: dict[int, list] = {}
        for a in all_assets:
            wid = wallet_per_asset[a.id]
            assets_by_wallet.setdefault(wid, []).append(a)
        wallet_tickers = {
            wid: [a.ticker_id for a in assets]
            for wid, assets in assets_by_wallet.items()
        }
        txn_pairs = await self.transaction_repo.wallets_tickers_with_transactions(wallet_tickers)
        for a in all_assets:
            a.has_transactions = (wallet_per_asset[a.id], a.ticker_id) in txn_pairs

    async def get_with_assets(self, id: int) -> Wallet:
        wallet = await self.service.get_with_assets(id)
        await self._enrich([wallet])
        await self._add_has_transactions([wallet])
        return wallet

    async def get_all_with_assets(self) -> list[Wallet]:
        wallets = await self.service.get_all_with_assets()
        await self._enrich(wallets)
        await self._add_has_transactions(wallets)
        return wallets
