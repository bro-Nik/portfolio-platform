from fastapi import APIRouter

from app.modules.market.dependencies import require_admin
from app.modules.market.routes.providers import providers_router
from app.modules.market.routes.tasks import tasks_router
from app.modules.market.routes.tickers import user_router

admin_router = APIRouter(prefix='/admin', dependencies=[require_admin])
admin_router.include_router(providers_router)
admin_router.include_router(tasks_router)

router = APIRouter()
router.include_router(user_router)
router.include_router(admin_router)
