from typing import Annotated

from fastapi import Query, Request

from app.common.exceptions import handle_errors
from app.common.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from app.core import settings
from app.core.rate_limit import limiter
from app.modules.market.dependencies import TickerServiceDep, require_user
from app.modules.market.routes.app_router import AppRouter
from app.modules.market.schemas import (
    ImagesResponse,
    PricesResponse,
    TickerInfoListResponse,
    TickerSearchResponse,
)

user_router = AppRouter(prefix='/api/tickers', tags=['User | Tickers'], dependencies=[require_user])


@user_router.get('')
@limiter.limit(settings.rate_limit_default)
@handle_errors('Ошибка получения тикеров')
async def search_tickers(
    request: Request,
    ticker_service: TickerServiceDep,
    search: str | None = Query(None),
    markets: Annotated[list[str] | None, Query()] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, alias='pageSize'),
) -> TickerSearchResponse:
    result = await ticker_service.search(search, markets, page, page_size)
    return TickerSearchResponse(**result)


@user_router.post('/prices')
@limiter.limit(settings.rate_limit_default)
@handle_errors('Ошибка получения цен')
async def get_prices(
    request: Request,
    ticker_ids: list[int],
    ticker_service: TickerServiceDep,
) -> PricesResponse:
    prices = await ticker_service.get_prices(ticker_ids)
    return PricesResponse(prices=prices)


@user_router.post('/images')
@limiter.limit(settings.rate_limit_default)
@handle_errors('Ошибка получения изображений')
async def get_images(
    request: Request,
    ticker_ids: list[int],
    ticker_service: TickerServiceDep,
) -> ImagesResponse:
    images = await ticker_service.get_images(ticker_ids)
    return ImagesResponse(images=images)


@user_router.post('/info')
@limiter.limit(settings.rate_limit_default)
@handle_errors('Ошибка получения информации о тикере')
async def get_info(
    request: Request,
    ticker_ids: list[int],
    ticker_service: TickerServiceDep,
) -> TickerInfoListResponse:
    info = await ticker_service.get_info(ticker_ids)
    return TickerInfoListResponse(info=info)
