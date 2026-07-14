from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository

from app.modules.portfolios.models import Portfolio


class PortfolioRepository(BaseRepository[Portfolio]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Portfolio, session)

    async def get_with_assets(self, id: int) -> Portfolio | None:
        return await self.get(id, relations=('assets',))

    async def get_all_by_user_with_assets(self, user_id: int) -> list[Portfolio]:
        return await self.get_all(Portfolio.user_id == user_id, relations=('assets',))

    async def exists_by_name_and_user(self, name: str, user_id: int) -> bool:
        return await self.exists_by(Portfolio.user_id == user_id, Portfolio.name == name)
