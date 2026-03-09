from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Wallet
from app.repositories import BaseRepository
from app.schemas import WalletCreate, WalletUpdate


class WalletRepository(BaseRepository[Wallet, WalletCreate, WalletUpdate]):
    """Репозиторий для работы с кошельками."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Wallet, session)

    async def get_with_assets(self, id: int) -> Wallet | None:
        """Получить кошелек с активами."""
        return await self.get(id, relations=('assets',))

    async def get_many_by_user_with_assets(self, user_id: int) -> list[Wallet]:
        """Получить кошельки пользователя."""
        return await self.get_many_by(Wallet.user_id == user_id, relations=('assets',))

    async def exists_by_name_and_user(self, name: str, user_id: int) -> bool:
        """Проверить, есть ли у пользователя кошелек с таким именем."""
        return await self.exists_by(
            Wallet.user_id == user_id,
            Wallet.name == name,
        )
