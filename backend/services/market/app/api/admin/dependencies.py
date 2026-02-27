from app.dependencies import DBSession
from app.services.api_provider import ApiProviderService
from app.services.api_task import ApiTaskService


async def get_api_provider_service(db: DBSession) -> ApiProviderService:
    return ApiProviderService(db)


async def get_api_task_service(db: DBSession) -> ApiTaskService:
    return ApiTaskService(db)
