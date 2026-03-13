from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task
from app.repositories.async_repo import BaseRepository
from app.schemas import TaskCreate, TaskUpdate


class TaskRepository(BaseRepository[Task, TaskCreate, TaskUpdate]):
    """Репозиторий для работы с API задачами."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Task, session)

    async def get_with_provider(self, id: int) -> Task:
        """Получить задачу с провайдером."""
        return await self.get(id, relations=['provider'])

    async def get_all_with_providers(self) -> list[Task]:
        """Получить все задачи с провайдерами."""
        return await self.get_all(relations=['provider'])

    async def exists_by_name(self, name: str) -> bool:
        """Проверить, есть ли задача с таким именем."""
        return await self.exists_by(Task.name == name)
