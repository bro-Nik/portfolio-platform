from fastapi import APIRouter

from app.api.admin.endpoints import user
from app.dependencies import require_admin

admin_router = APIRouter(prefix='/admin', dependencies=[require_admin])

admin_router.include_router(user.router)
