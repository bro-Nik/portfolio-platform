from fastapi import APIRouter

from .watchlist import router as watchlist_router

router = APIRouter()
router.include_router(watchlist_router)
