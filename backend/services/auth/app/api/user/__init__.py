from fastapi import APIRouter, Depends

from app.api.user.endpoints import profile
from app.dependencies import require_role
from app.schemas import UserRole

user_router = APIRouter(dependencies=[Depends(require_role(UserRole.USER))])

user_router.include_router(profile.router)
