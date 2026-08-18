from fastapi import Request

from app.common.exceptions import handle_errors
from app.core import settings
from app.core.rate_limit import limiter
from app.modules.market.dependencies import TickerServiceDep
from app.modules.market.routes.app_router import AppRouter
from app.modules.market.schemas import TickerDetailResponse, TickerListResponse, TickerMergeRequest, TickerUpdateRequest

admin_tickers_router = AppRouter(prefix='/tickers', tags=['Admin | Tickers'])


@admin_tickers_router.get('')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения тикеров')
async def list_tickers(
    request: Request,
    service: TickerServiceDep,
    search: str | None = None,
    markets: list[str] | None = None,
    page: int = 1,
    page_size: int = 20,
) -> TickerListResponse:
    return await service.get_all_admin(search=search, markets=markets, page=page, page_size=page_size)


@admin_tickers_router.get('/{ticker_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения тикера')
async def get_ticker(
    request: Request,
    ticker_id: int,
    service: TickerServiceDep,
) -> TickerDetailResponse:
    return await service.get(ticker_id)


@admin_tickers_router.put('/{ticker_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка обновления тикера')
async def update_ticker(
    request: Request,
    ticker_id: int,
    data: TickerUpdateRequest,
    service: TickerServiceDep,
) -> TickerDetailResponse:
    return await service.update(ticker_id, data)


@admin_tickers_router.delete('/{ticker_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления тикера')
async def delete_ticker(
    request: Request,
    ticker_id: int,
    service: TickerServiceDep,
) -> None:
    await service.delete(ticker_id)


@admin_tickers_router.post('/merge')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка слияния тикеров')
async def merge_tickers(
    request: Request,
    data: TickerMergeRequest,
    service: TickerServiceDep,
) -> TickerDetailResponse:
    return await service.merge(data.source_id, data.target_id)
