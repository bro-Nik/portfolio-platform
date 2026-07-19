from fastapi import APIRouter, Request

from app.common.exceptions import handle_errors
from app.core.rate_limit import limiter

from app.core import settings
from app.modules.portfolios.dependencies import (
    PortfolioAssetServiceDep, PortfolioReadQueryDep, PortfolioServiceDep,
    TransactionReadQueryDep,
    require_user,
)
from app.modules.portfolios.schemas import (
    PortfolioAssetCreateRequest, PortfolioCreateRequest, PortfolioDeleteResponse,
    PortfolioListResponse, PortfolioResponse, PortfolioUpdateRequest,
    TransactionResponse,
)


router = APIRouter(dependencies=[require_user])


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


@router.delete('/portfolios/{portfolio_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления портфеля')
async def delete_portfolio(
    request: Request,
    portfolio_id: int,
    portfolio_service: PortfolioServiceDep,
) -> PortfolioDeleteResponse:
    await portfolio_service.delete(portfolio_id)
    return PortfolioDeleteResponse(portfolio_id=portfolio_id)


@router.post('/portfolios/{portfolio_id}/archive')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка архивации портфеля')
async def archive_portfolio(
    request: Request,
    portfolio_id: int,
    portfolio_service: PortfolioServiceDep,
) -> PortfolioDeleteResponse:
    await portfolio_service.archive(portfolio_id)
    return PortfolioDeleteResponse(portfolio_id=portfolio_id)


@router.post('/portfolios/{portfolio_id}/unarchive')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка разархивации портфеля')
async def unarchive_portfolio(
    request: Request,
    portfolio_id: int,
    portfolio_service: PortfolioServiceDep,
) -> PortfolioDeleteResponse:
    await portfolio_service.unarchive(portfolio_id)
    return PortfolioDeleteResponse(portfolio_id=portfolio_id)


@router.post('/portfolios/{portfolio_id}/assets', status_code=201)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка добавления актива')
async def add_asset_to_portfolio(
    request: Request,
    portfolio_id: int,
    data: PortfolioAssetCreateRequest,
    portfolio_service: PortfolioServiceDep,
    query: PortfolioReadQueryDep,
) -> PortfolioResponse:
    await portfolio_service.add_asset(portfolio_id, data)
    return await query.get_with_assets(portfolio_id)


@router.delete('/portfolios/{portfolio_id}/assets/{asset_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления актива')
async def delete_asset_from_portfolio(
    request: Request,
    portfolio_id: int,
    asset_id: int,
    portfolio_service: PortfolioServiceDep,
    query: PortfolioReadQueryDep,
) -> PortfolioResponse:
    await portfolio_service.delete_asset(portfolio_id, asset_id)
    return await query.get_with_assets(portfolio_id)


@router.post('/portfolios/{portfolio_id}/assets/{asset_id}/archive')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка архивации актива')
async def archive_asset_in_portfolio(
    request: Request,
    portfolio_id: int,
    asset_id: int,
    portfolio_service: PortfolioServiceDep,
    query: PortfolioReadQueryDep,
) -> PortfolioResponse:
    await portfolio_service.archive_asset(portfolio_id, asset_id)
    return await query.get_with_assets(portfolio_id)


@router.post('/portfolios/{portfolio_id}/assets/{asset_id}/unarchive')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка разархивации актива')
async def unarchive_asset_in_portfolio(
    request: Request,
    portfolio_id: int,
    asset_id: int,
    portfolio_service: PortfolioServiceDep,
    query: PortfolioReadQueryDep,
) -> PortfolioResponse:
    await portfolio_service.unarchive_asset(portfolio_id, asset_id)
    return await query.get_with_assets(portfolio_id)


@router.get('/portfolios/assets/{asset_id}/transactions')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения транзакций актива')
async def get_asset_transactions(
    request: Request,
    asset_id: int,
    query: TransactionReadQueryDep,
) -> list[TransactionResponse]:
    return await query.get_portfolio_asset_transactions(asset_id)


@router.get('/portfolios/assets/{asset_id}/distribution')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения распределения актива')
async def get_asset_distribution(
    request: Request,
    asset_id: int,
    asset_service: PortfolioAssetServiceDep,
) -> dict:
    return await asset_service.get_distribution(asset_id)
