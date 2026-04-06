from fastapi import APIRouter

from app.api.admin.endpoints import providers, tasks
from app.dependencies import require_admin

admin_router = APIRouter(prefix='/admin', dependencies=[require_admin])


admin_router.include_router(providers.router)
admin_router.include_router(tasks.router)
