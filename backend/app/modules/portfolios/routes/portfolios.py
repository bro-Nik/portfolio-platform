from fastapi import Request

from app.common.routing import DishkaRouter

from app.common.exceptions import handle_errors
from app.core.rate_limit import limiter

from app.core import settings
from app.modules.portfolios.dependencies import (
    PortfolioAssetServiceDep, PortfolioReadQueryDep, PortfolioServiceDep,
    TransactionReadQueryDep,
    require_user,
)
from app.modules.portfolios.schemas import (
    PortfolioAssetArchiveRequest, PortfolioAssetCreateRequest, PortfolioAssetResponse,
    PortfolioArchiveRequest, PortfolioCreateRequest,
    PortfolioListResponse, PortfolioResponse, PortfolioUpdateRequest,
    TransactionResponse,
)


router = DishkaRouter(dependencies=[require_user])


@router.get('/portfolios')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения портфелей')
async def get_user_portfolios(
    request: Request,
    query: PortfolioReadQueryDep,
) -> PortfolioListResponse:
    portfolios = await query.get_all_with_assets()
    return PortfolioListResponse(portfolios=portfolios)


@router.get('/portfolios/{portfolio_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения портфеля')
async def get_user_portfolio(
    request: Request,
    portfolio_id: int,
    query: PortfolioReadQueryDep,
) -> PortfolioResponse:
    return await query.get_with_assets(portfolio_id)


@router.post('/portfolios', status_code=201)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка создания портфеля')
async def create_portfolio(
    request: Request,
    data: PortfolioCreateRequest,
    portfolio_service: PortfolioServiceDep,
    query: PortfolioReadQueryDep,
) -> PortfolioResponse:
    portfolio = await portfolio_service.create(data)
    return await query.get_with_assets(portfolio.id)


@router.put('/portfolios/{portfolio_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка обновления портфеля')
async def update_portfolio(
    request: Request,
    portfolio_id: int,
    data: PortfolioUpdateRequest,
    portfolio_service: PortfolioServiceDep,
    query: PortfolioReadQueryDep,
) -> PortfolioResponse:
    portfolio = await portfolio_service.update(portfolio_id, data)
    return await query.get_with_assets(portfolio.id)


@router.delete('/portfolios/{portfolio_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления портфеля')
async def delete_portfolio(
    request: Request,
    portfolio_id: int,
    portfolio_service: PortfolioServiceDep,
) -> None:
    await portfolio_service.delete(portfolio_id)


@router.patch('/portfolios/{portfolio_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка изменения статуса портфеля')
async def set_portfolio_archived(
    request: Request,
    portfolio_id: int,
    data: PortfolioArchiveRequest,
    portfolio_service: PortfolioServiceDep,
) -> None:
    await portfolio_service.set_archived(portfolio_id, data.is_archived)


@router.post('/portfolios/{portfolio_id}/assets', status_code=201)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка добавления актива')
async def add_asset_to_portfolio(
    request: Request,
    portfolio_id: int,
    data: PortfolioAssetCreateRequest,
    portfolio_service: PortfolioServiceDep,
    query: PortfolioReadQueryDep,
) -> PortfolioAssetResponse:
    asset = await portfolio_service.add_asset(portfolio_id, data)
    await query.enrich_single_asset(asset)
    return PortfolioAssetResponse.model_validate(asset)


@router.delete('/portfolios/{portfolio_id}/assets/{asset_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления актива')
async def delete_asset_from_portfolio(
    request: Request,
    portfolio_id: int,
    asset_id: int,
    portfolio_service: PortfolioServiceDep,
) -> None:
    await portfolio_service.delete_asset(portfolio_id, asset_id)


@router.patch('/portfolios/{portfolio_id}/assets/{asset_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка изменения статуса актива')
async def set_asset_in_portfolio_archived(
    request: Request,
    portfolio_id: int,
    asset_id: int,
    data: PortfolioAssetArchiveRequest,
    portfolio_service: PortfolioServiceDep,
) -> None:
    await portfolio_service.set_asset_archived(portfolio_id, asset_id, data.is_archived)


@router.get('/portfolios/{portfolio_id}/assets/{asset_id}/transactions')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения транзакций актива')
async def get_asset_transactions(
    request: Request,
    portfolio_id: int,
    asset_id: int,
    query: TransactionReadQueryDep,
) -> list[TransactionResponse]:
    return await query.get_portfolio_asset_transactions(asset_id)


@router.get('/portfolios/{portfolio_id}/assets/{asset_id}/distribution')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения распределения актива')
async def get_asset_distribution(
    request: Request,
    portfolio_id: int,
    asset_id: int,
    asset_service: PortfolioAssetServiceDep,
) -> dict:
    return await asset_service.get_distribution(asset_id)
