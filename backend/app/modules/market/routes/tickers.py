
from fastapi import Query

from app.common.exceptions import handle_errors

from app.modules.market.dependencies import TickerServiceDep, require_user
from app.modules.market.schemas import (
    ImagesResponse, PricesResponse,
    TickerInfoListResponse, TickerSearchResponse,
)
from app.modules.market.routes.app_router import AppRouter


user_router = AppRouter(prefix='/api/tickers', tags=['User | Tickers'], dependencies=[require_user])


@user_router.get('')
@handle_errors('Ошибка получения тикеров')
async def search_tickers(
    ticker_service: TickerServiceDep,
    search: str | None = Query(None),
    market: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> TickerSearchResponse:
    result = await ticker_service.search(search, market, page, page_size)
    return TickerSearchResponse(**result)


@user_router.post('/prices')
@handle_errors('Ошибка получения цен')
async def get_prices(
    ticker_ids: list[int],
    ticker_service: TickerServiceDep,
) -> PricesResponse:
    prices = await ticker_service.get_prices(ticker_ids)
    return PricesResponse(prices=prices)


@user_router.post('/images')
@handle_errors('Ошибка получения изображений')
async def get_images(
    ticker_ids: list[int],
    ticker_service: TickerServiceDep,
) -> ImagesResponse:
    images = await ticker_service.get_images(ticker_ids)
    return ImagesResponse(images=images)


@user_router.post('/info')
@handle_errors('Ошибка получения информации о тикере')
async def get_info(
    ticker_ids: list[int],
    ticker_service: TickerServiceDep,
) -> TickerInfoListResponse:
    info = await ticker_service.get_info(ticker_ids)
    return TickerInfoListResponse(info=info)
