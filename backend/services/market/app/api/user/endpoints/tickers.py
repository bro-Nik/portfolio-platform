"""Тикеры.

Все эндпоинты требуют валидный access token
В некоторых эндпоинтах используется POST вместо GET для передачи большого количества ID
"""

from fastapi import Query

from app.api.router import AppRouter
from app.dependencies import TickerServiceDep
from app.schemas import ImagesResponse, PricesResponse, TickerInfoListResponse, TickerSearchResponse
from shared.exceptions import handle_errors

router = AppRouter(prefix='/tickers', tags=['User | Tickers'])


@router.get('')
@handle_errors('Ошибка при получении тикеров')
async def search_tickers(
    ticker_service: TickerServiceDep,
    search: str | None = Query(None, description='Поиск по названию или символу'),
    market: str | None = Query(None, description='Рынок (crypto, stock, currency)'),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> TickerSearchResponse:
    """Поиск тикеров с пагинацией и фильтрацией."""
    result = await ticker_service.search(search, market, page, page_size)
    return TickerSearchResponse(**result)


@router.post('/prices')
@handle_errors('Ошибка при получении цен')
async def get_prices(
    ticker_ids: list[str],
    ticker_service: TickerServiceDep,
) -> PricesResponse:
    """Возвращает текущие цены для списка активов."""
    prices = await ticker_service.get_prices(ticker_ids)
    return PricesResponse(prices=prices)


@router.post('/images')
@handle_errors('Ошибка при получении изображений')
async def get_images(
    ticker_ids: list[str],
    ticker_service: TickerServiceDep,
) -> ImagesResponse:
    """Возвращает URL изображений для списка активов."""
    images = await ticker_service.get_images(ticker_ids)
    return ImagesResponse(images=images)


@router.post('/info')
@handle_errors('Ошибка при получении информации о тикерах')
async def get_info(
    ticker_ids: list[str],
    ticker_service: TickerServiceDep,
) -> TickerInfoListResponse:
    """Возвращает информацию о тикерах для списка активов."""
    info = await ticker_service.get_info(ticker_ids)
    return TickerInfoListResponse(info=info)
