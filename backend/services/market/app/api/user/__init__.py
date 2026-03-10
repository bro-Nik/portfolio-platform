from fastapi import APIRouter

from app.api.user.endpoints import tickers
from app.dependencies import require_user

user_router = APIRouter(prefix='/api', dependencies=[require_user])


user_router.include_router(tickers.router)
