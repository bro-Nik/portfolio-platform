from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Task
from app.repositories import TaskRepository
from app.schemas import TaskCreateRequest, TaskUpdateRequest
from shared.exceptions import ConflictError, NotFoundError


class TaskService:
    """Сервис для работы с API задачами."""

    def __init__(self, session: AsyncSession, task_repo: TaskRepository) -> None:
        self.session = session
        self.repo = task_repo

    async def get_all(self) -> list[Task]:
        """Получить список задач."""
        return await self.repo.get_all()

    async def get_all_with_providers(self) -> list[Task]:
        """Получить список задач с провайдерами."""
        return await self.repo.get_all_with_providers()

    async def get_all_active_with_providers(self) -> list[Task]:
        """Получить список активных задач с провайдерами."""
        return await self.repo.get_all_active_with_providers()

    async def get(self, id: int) -> Task:
        """Получить задачу по ID."""
        task = await self.repo.get(id)
        self._verify(task)
        return task

    async def get_with_provider(self, id: int) -> Task:
        """Получить задачу с провайдером."""
        task = await self.repo.get_with_provider(id)
        self._verify(task)
        return task

    async def create(self, data: TaskCreateRequest) -> Task:
        """Создать задачу."""
        await self._validate_create_data(data)

        task = await self.repo.create(data)
        await self.session.flush()
        return task

    async def update(self, id: int, data: TaskUpdateRequest) -> Task:
        """Обновить задачу."""
        task = await self.get(id)
        await self._validate_update_data(data, task)
        return await self.repo.update(id, data)

    async def delete(self, id: int) -> Task | None:
        """Удалить задачу."""
        await self.repo.delete(id)

    def _verify(self, task: Task) -> None:
        if not task:
            raise NotFoundError('API задача не найдена')

    async def _validate_create_data(self, data: TaskCreateRequest) -> None:
        await self._validate_unique_name(data.name)

    async def _validate_update_data(self, data: TaskUpdateRequest, task: Task) -> None:
        if data.name and data.name != task.name:
            await self._validate_unique_name(data.name)

    async def _validate_unique_name(self, name: str) -> None:
        if await self.repo.exists_by_name(name):
            raise ConflictError(f'API задача с именем "{name}" уже существует')
