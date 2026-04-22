from sqlalchemy.ext.asyncio import AsyncSession

from shared.repositories import BaseRepository

from app.models import Portfolio


class PortfolioRepository(BaseRepository[Portfolio]):
    """Репозиторий для работы с портфелями."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Portfolio, session)

    async def get_with_assets(self, id: int) -> Portfolio | None:
        """Получить портфель с активами."""
        return await self.get(id, relations=('assets',))

    async def get_all_by_user_with_assets(self, user_id: int) -> list[Portfolio]:
        """Получить портфели пользователя."""
        return await self.get_all(Portfolio.user_id == user_id, relations=('assets',))

    async def exists_by_name_and_user(self, name: str, user_id: int) -> bool:
        """Проверить, есть ли у пользователя портфель с таким именем."""
        return await self.exists_by(
            Portfolio.user_id == user_id,
            Portfolio.name == name,
        )
