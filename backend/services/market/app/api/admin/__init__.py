from fastapi import APIRouter

from app.api.admin.endpoints import api_providers, api_tasks
from app.dependencies import require_admin

admin_router = APIRouter(prefix='/admin', dependencies=[require_admin])


admin_router.include_router(api_providers.router)
admin_router.include_router(api_tasks.router)
