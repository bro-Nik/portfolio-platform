from typing import Annotated

from fastapi import Depends

from app.dependencies import DBSession
from app.services import ApiProviderService, ApiTaskService


async def get_api_provider_service(db: DBSession) -> ApiProviderService:
    """Зависимость для получения сервиса API провайдеров."""
    return ApiProviderService(db)


async def get_api_task_service(db: DBSession) -> ApiTaskService:
    """Зависимость для получения сервиса API задач."""
    return ApiTaskService(db)


ApiProviderServiceDep = Annotated[ApiProviderService, Depends(get_api_provider_service)]
ApiTaskServiceDep = Annotated[ApiTaskService, Depends(get_api_task_service)]
