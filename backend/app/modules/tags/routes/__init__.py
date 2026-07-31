from fastapi import APIRouter

from .tags import router as tags_router

router = APIRouter()
router.include_router(tags_router)
