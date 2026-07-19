from fastapi import APIRouter, Request

from app.common.exceptions import handle_errors
from app.core.rate_limit import limiter

from app.core import settings
from app.modules.portfolios.dependencies import OverviewReadQueryDep, require_user
from app.modules.portfolios.schemas.overview import OverviewResponse


router = APIRouter(dependencies=[require_user])


@router.get('/overview')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения общих данных')
async def get_user_overview(
    request: Request,
    query: OverviewReadQueryDep,
) -> OverviewResponse:
    portfolios, wallets = await query.get_all()
    return OverviewResponse(portfolios=portfolios, wallets=wallets)
