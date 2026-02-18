from fastapi import APIRouter, Depends

from app.api.admin.endpoints import user
from app.dependencies import require_role
from app.schemas import UserRole

admin_router = APIRouter(prefix='/admin', dependencies=[Depends(require_role(UserRole.ADMIN))])

admin_router.include_router(user.router)
