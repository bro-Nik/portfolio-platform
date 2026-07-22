from app.common.exceptions import handle_errors
from app.modules.market.dependencies import TickerAdminServiceDep
from app.modules.market.schemas import TickerAdminResponse, TickerMergeRequest, TickerUpdateRequest
from app.modules.market.routes.app_router import AppRouter


admin_tickers_router = AppRouter(prefix='/tickers', tags=['Admin | Tickers'])


@admin_tickers_router.get('')
@handle_errors('Ошибка получения тикеров')
async def list_tickers(
    service: TickerAdminServiceDep,
    search: str | None = None,
    market: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    return await service.list(search=search, market=market, page=page, page_size=page_size)


@admin_tickers_router.get('/{ticker_id}')
@handle_errors('Ошибка получения тикера')
async def get_ticker(ticker_id: int, service: TickerAdminServiceDep) -> TickerAdminResponse:
    return await service.get_by_id(ticker_id)


@admin_tickers_router.put('/{ticker_id}')
@handle_errors('Ошибка обновления тикера')
async def update_ticker(ticker_id: int, data: TickerUpdateRequest, service: TickerAdminServiceDep) -> TickerAdminResponse:
    return await service.update(ticker_id, data)


@admin_tickers_router.delete('/{ticker_id}', status_code=204)
@handle_errors('Ошибка удаления тикера')
async def delete_ticker(ticker_id: int, service: TickerAdminServiceDep) -> None:
    await service.delete(ticker_id)


@admin_tickers_router.post('/merge')
@handle_errors('Ошибка слияния тикеров')
async def merge_tickers(data: TickerMergeRequest, service: TickerAdminServiceDep) -> TickerAdminResponse:
    return await service.merge(data.source_id, data.target_id)
