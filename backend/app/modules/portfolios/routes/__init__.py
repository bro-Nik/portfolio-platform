from fastapi import APIRouter

from .internal import router as internal_router
from .portfolios import router as portfolios_router
from .tags import router as tags_router
from .transactions import router as transactions_router
from .wallets import router as wallets_router

router = APIRouter()
router.include_router(portfolios_router)
router.include_router(wallets_router)
router.include_router(transactions_router)
router.include_router(tags_router)
router.include_router(internal_router)
