from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.services.api_provider import ApiProviderService
from app.services.api_task import ApiTaskService


async def get_api_provider_service(db: AsyncSession = Depends(get_db)) -> ApiProviderService:
    return ApiProviderService(db)


async def get_api_task_service(db: AsyncSession = Depends(get_db)) -> ApiTaskService:
    return ApiTaskService(db)
