from fastapi import APIRouter

from .overview import router as overview_router
from .portfolios import router as portfolios_router
from .transactions import router as transactions_router
from .wallets import router as wallets_router

router = APIRouter()
router.include_router(overview_router)
router.include_router(portfolios_router)
router.include_router(wallets_router)
router.include_router(transactions_router)
