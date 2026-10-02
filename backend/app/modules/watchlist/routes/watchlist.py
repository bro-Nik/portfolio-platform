from fastapi import Request

from app.common.exceptions import handle_errors
from app.common.routing import DishkaRouter
from app.core import settings
from app.core.rate_limit import limiter
from app.modules.watchlist.dependencies import (
    AlertServiceDep,
    WatchlistServiceDep,
    require_user,
)
from app.modules.watchlist.schemas import (
    PriceAlertArchiveRequest,
    PriceAlertCreate,
    PriceAlertResponse,
    PriceAlertUpdate,
    TriggeredAlertListResponse,
    WatchlistItemArchiveRequest,
    WatchlistItemCreate,
    WatchlistItemResponse,
    WatchlistItemUpdate,
    WatchlistListResponse,
)

router = DishkaRouter(dependencies=[require_user])


@router.get('/watchlist/alerts/triggered')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения сработавших уведомлений')
async def get_triggered_alerts(
    request: Request,
    alert_service: AlertServiceDep,
) -> TriggeredAlertListResponse:
    return TriggeredAlertListResponse(alerts=await alert_service.get_triggered())


@router.get('/watchlist')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения избранного')
async def get_watchlist(
    request: Request,
    watchlist_service: WatchlistServiceDep,
) -> WatchlistListResponse:
    return WatchlistListResponse(items=await watchlist_service.get_all())


@router.post('/watchlist', status_code=201)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка добавления в избранное')
async def add_watchlist_item(
    request: Request,
    data: WatchlistItemCreate,
    watchlist_service: WatchlistServiceDep,
) -> WatchlistItemResponse:
    return await watchlist_service.create(data.ticker_id, data.comment)


@router.put('/watchlist/{item_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка обновления записи избранного')
async def update_watchlist_item(
    request: Request,
    item_id: int,
    data: WatchlistItemUpdate,
    watchlist_service: WatchlistServiceDep,
) -> WatchlistItemResponse:
    return await watchlist_service.update(item_id, data.comment)


@router.delete('/watchlist/{item_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления записи избранного')
async def delete_watchlist_item(
    request: Request,
    item_id: int,
    watchlist_service: WatchlistServiceDep,
) -> None:
    await watchlist_service.delete(item_id)


@router.patch('/watchlist/{item_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка изменения статуса записи избранного')
async def set_watchlist_item_archived(
    request: Request,
    item_id: int,
    data: WatchlistItemArchiveRequest,
    watchlist_service: WatchlistServiceDep,
) -> None:
    await watchlist_service.archive(item_id, data.is_archived)


@router.get('/watchlist/{item_id}/alerts')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения уведомлений')
async def get_item_alerts(
    request: Request,
    item_id: int,
    alert_service: AlertServiceDep,
) -> list[PriceAlertResponse]:
    return await alert_service.get_by_item(item_id)


@router.post('/watchlist/{item_id}/alerts', status_code=201)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка создания уведомления')
async def create_alert(
    request: Request,
    item_id: int,
    data: PriceAlertCreate,
    alert_service: AlertServiceDep,
) -> PriceAlertResponse:
    return await alert_service.create(
        item_id,
        direction=data.direction,
        target_price_usd=data.target_price_usd,
        currency_symbol=data.currency_symbol,
        comment=data.comment,
    )


@router.put('/watchlist/alerts/{alert_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка обновления уведомления')
async def update_alert(
    request: Request,
    alert_id: int,
    data: PriceAlertUpdate,
    alert_service: AlertServiceDep,
) -> PriceAlertResponse:
    return await alert_service.update(
        alert_id,
        direction=data.direction,
        target_price_usd=data.target_price_usd,
        currency_symbol=data.currency_symbol,
        comment=data.comment,
        is_active=data.is_active,
    )


@router.delete('/watchlist/alerts/{alert_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления уведомления')
async def delete_alert(
    request: Request,
    alert_id: int,
    alert_service: AlertServiceDep,
) -> None:
    await alert_service.delete(alert_id)


@router.patch('/watchlist/alerts/{alert_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка изменения статуса уведомления')
async def set_alert_archived(
    request: Request,
    alert_id: int,
    data: PriceAlertArchiveRequest,
    alert_service: AlertServiceDep,
) -> None:
    await alert_service.archive(alert_id, data.is_archived)
