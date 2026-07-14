from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository

from app.modules.market.models import Provider


class ProviderRepository(BaseRepository[Provider]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Provider, session)

    async def get_all_active(self) -> list[Provider]:
        return await self.get_all(Provider.is_active)

    async def get_by_name(self, name: str) -> Provider | None:
        return await self.get_by(Provider.name == name)

    async def exists_by_name(self, name: str) -> bool:
        return await self.exists_by(Provider.name.ilike(name))
