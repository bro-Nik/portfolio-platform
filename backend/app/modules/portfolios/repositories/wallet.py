from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository

from app.modules.portfolios.models import Wallet


class WalletRepository(BaseRepository[Wallet]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Wallet, session)

    async def get_with_assets(self, id: int) -> Wallet | None:
        return await self.get(id, relations=('assets',))

    async def get_all_by_user_with_assets(self, user_id: int) -> list[Wallet]:
        return await self.get_all(Wallet.user_id == user_id, relations=('assets',))

    async def exists_by_name_and_user(self, name: str, user_id: int) -> bool:
        return await self.exists_by(Wallet.user_id == user_id, Wallet.name == name)
