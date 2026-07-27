from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository

from app.modules.market.models import Task


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Task, session)

    async def exists_by_name(self, name: str) -> bool:
        return await self.exists_by(Task.name == name)

    async def get_all_active(self) -> list[Task]:
        return await self.get_all(Task.is_active)

    async def get_active_by_status(self, status: str) -> list[Task]:
        return await self.get_all(Task.is_active, Task.status == status)
