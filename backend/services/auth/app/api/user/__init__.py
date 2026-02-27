from fastapi import APIRouter

from app.api.user.endpoints import profile
from app.dependencies import require_user

user_router = APIRouter(dependencies=[require_user])

user_router.include_router(profile.router)
