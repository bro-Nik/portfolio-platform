from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WalletAsset
from app.repositories import BaseRepository
from app.schemas import WalletAssetCreate, WalletAssetUpdate


class WalletAssetRepository(BaseRepository[WalletAsset, WalletAssetCreate, WalletAssetUpdate]):
    """Репозиторий для работы с активами кошельков."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(WalletAsset, session)

    async def get_by_ticker_and_wallet(self, ticker_id: str, wallet_id: int) -> WalletAsset | None:
        """Получить актив кошелька по тикеру."""
        return await self.get_by(
            WalletAsset.wallet_id == wallet_id,
            WalletAsset.ticker_id == ticker_id,
        )

    async def get_many_by_ticker_and_user_with_wallets(self, ticker_id: str, user_id: int) -> list[WalletAsset]:
        """Получить активы пользователя по тикеру."""
        return await self.get_many_by(
            WalletAsset.ticker_id == ticker_id,
            WalletAsset.user_id == user_id,
            relations=('wallet',),
        )

    async def get_many_by_tickers_and_wallet(self, ticker_ids: list[str], wallet_id: int) -> list[WalletAsset]:
        """Получить активы кошелька по списку тикеров."""
        return await self.get_many_by(
            WalletAsset.wallet_id == wallet_id,
            WalletAsset.ticker_id.in_(ticker_ids),
        )
