from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository

from app.modules.portfolios.models import WalletAsset


class WalletAssetRepository(BaseRepository[WalletAsset]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(WalletAsset, session)

    async def get_by_ticker_and_wallet(self, ticker_id: int, wallet_id: int) -> WalletAsset | None:
        return await self.get_by(WalletAsset.wallet_id == wallet_id, WalletAsset.ticker_id == ticker_id)

    async def get_all_by_ticker_and_user_with_wallets(self, ticker_id: int, user_id: int) -> list[WalletAsset]:
        return await self.get_all(WalletAsset.ticker_id == ticker_id, WalletAsset.user_id == user_id, relations=('wallet',))

    async def get_all_by_tickers_and_wallet(self, ticker_ids: list[int], wallet_id: int) -> list[WalletAsset]:
        return await self.get_all(WalletAsset.wallet_id == wallet_id, WalletAsset.ticker_id.in_(ticker_ids))
