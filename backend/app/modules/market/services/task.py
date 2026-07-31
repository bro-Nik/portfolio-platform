from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BusinessRuleError, ConflictError, NotFoundError

from app.modules.market.external_api.core import registry
from app.modules.market.models import Task
from app.modules.market.repositories import ProviderRepository, TaskRepository
from app.modules.market.schemas import (
    TaskCreate, TaskCreateRequest, TaskUpdate, TaskUpdateRequest,
)


class TaskService:
    def __init__(self, session: AsyncSession, task_repo: TaskRepository, provider_repo: ProviderRepository) -> None:
        self.session = session
        self.repo = task_repo
        self.provider_repo = provider_repo

    async def get_all(self) -> list[Task]:
        return await self.repo.get_all()

    async def get(self, id: int) -> Task:
        task = await self.repo.get(id)
        if not task:
            raise NotFoundError('API задача не найдена')
        return task

    async def _validate_provider_active(self, provider_name: str) -> None:
        if provider_name not in registry.PROVIDERS:
            raise NotFoundError(f'API провайдер "{provider_name}" не зарегистрирован')
        provider = await self.provider_repo.get_by_name(provider_name)
        if not provider:
            raise NotFoundError(f'API провайдер "{provider_name}" не найден')
        if not provider.is_active:
            raise BusinessRuleError(f'API провайдер "{provider_name}" неактивен. Сначала настройте и активируйте провайдера.')

    async def create(self, data: TaskCreateRequest) -> Task:
        if await self.repo.exists_by_name(data.name):
            raise ConflictError(f'API задача с именем "{data.name}" уже существует')
        await self._validate_provider_active(data.provider_name)
        task = await self.repo.create(TaskCreate(**data.model_dump()).model_dump())
        await self.session.commit()
        return task

    async def update(self, id: int, data: TaskUpdateRequest) -> Task:
        task = await self.get(id)
        if data.name and data.name != task.name:
            if await self.repo.exists_by_name(data.name):
                raise ConflictError(f'API задача с именем "{data.name}" уже существует')
        if data.provider_name and data.provider_name != task.provider_name:
            await self._validate_provider_active(data.provider_name)
        updated = await self.repo.update(id, TaskUpdate(**data.model_dump()).model_dump())
        await self.session.commit()
        return updated

    async def delete(self, id: int) -> None:
        await self.repo.delete(id)
        await self.session.commit()
