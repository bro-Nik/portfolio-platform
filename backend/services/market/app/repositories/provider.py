from sqlalchemy.ext.asyncio import AsyncSession

from shared.repositories import BaseRepository

from app.models import Provider


class ProviderRepository(BaseRepository[Provider]):
    """Репозиторий для работы с API провайдерами."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Provider, session)

    async def get_all_active(self) -> list[Provider]:
        """Получить активные API провайдеры."""
        return await self.get_all(Provider.is_active == True)

    async def get_by_name(self, name: str) -> Provider | None:
        """Получить API провайдера по названию."""
        return await self.get_by(Provider.name == name)

    async def exists_by_name(self, name: str) -> bool:
        """Проверить, есть ли провайдер с таким именем (без учета регистра)."""
        return await self.exists_by(Provider.name.ilike(name))
