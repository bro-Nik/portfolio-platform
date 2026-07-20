from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictError, NotFoundError

from app.modules.market.models import Task
from app.modules.market.repositories import TaskRepository
from app.modules.market.schemas import (
    TaskCreate, TaskCreateRequest, TaskUpdate, TaskUpdateRequest,
)


class TaskService:
    def __init__(self, session: AsyncSession, task_repo: TaskRepository) -> None:
        self.session = session
        self.repo = task_repo

    async def get_all(self) -> list[Task]:
        return await self.repo.get_all()

    async def get(self, id: int) -> Task:
        task = await self.repo.get(id)
        if not task:
            raise NotFoundError('API задача не найдена')
        return task

    async def create(self, data: TaskCreateRequest) -> Task:
        if await self.repo.exists_by_name(data.name):
            raise ConflictError(f'API задача с именем "{data.name}" уже существует')
        task = await self.repo.create(TaskCreate(**data.model_dump()).model_dump())
        await self.session.flush()
        return task

    async def update(self, id: int, data: TaskUpdateRequest) -> Task:
        task = await self.get(id)
        if data.name and data.name != task.name:
            if await self.repo.exists_by_name(data.name):
                raise ConflictError(f'API задача с именем "{data.name}" уже существует')
        return await self.repo.update(id, TaskUpdate(**data.model_dump()).model_dump())

    async def delete(self, id: int) -> None:
        await self.repo.delete(id)
