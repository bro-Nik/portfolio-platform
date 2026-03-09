"""Портфели пользователя и их активы.

Все эндпоинты требуют валидный access token
"""

from fastapi import APIRouter, Request
from shared.api import responses
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.core import settings
from app.dependencies import PortfolioAssetServiceDep, PortfolioServiceDep
from app.schemas import (
    PortfolioAssetCreateRequest,
    PortfolioCreateRequest,
    PortfolioDeleteResponse,
    PortfolioListResponse,
    PortfolioResponse,
    PortfolioUpdateRequest,
    TransactionResponse,
)

router = APIRouter(prefix='/portfolios', tags=['Portfolios'], responses=responses(401, 429, 500))


@router.get('/')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении портфелей')
async def get_user_portfolios(
    request: Request,
    portfolio_service: PortfolioServiceDep,
) -> PortfolioListResponse:
    """Получение всех портфелей пользователя."""
    portfolios = await portfolio_service.get_many_with_assets()
    return PortfolioListResponse(portfolios=portfolios)


@router.get('/{portfolio_id}', responses=responses(404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении портфеля')
async def get_user_portfolio(
    request: Request,
    portfolio_id: int,
    portfolio_service: PortfolioServiceDep,
) -> PortfolioResponse:
    """Получение портфеля пользователя."""
    return await portfolio_service.get_with_assets(portfolio_id)


@router.post('/', status_code=201, responses=responses(400, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при создании портфеля')
async def create_portfolio(
    request: Request,
    data: PortfolioCreateRequest,
    portfolio_service: PortfolioServiceDep,
) -> PortfolioResponse:
    """Создание нового портфеля."""
    portfolio = await portfolio_service.create(data)
    return await portfolio_service.get_with_assets(portfolio.id)


@router.put('/{portfolio_id}', responses=responses(400, 404, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при изменении портфеля')
async def update_portfolio(
    request: Request,
    portfolio_id: int,
    data: PortfolioUpdateRequest,
    portfolio_service: PortfolioServiceDep,
) -> PortfolioResponse:
    """Обновление портфеля."""
    portfolio = await portfolio_service.update(portfolio_id, data)
    return await portfolio_service.get_with_assets(portfolio.id)


@router.delete('/{portfolio_id}', responses=responses(400, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при удалении портфеля')
async def delete_portfolio(
    request: Request,
    portfolio_id: int,
    portfolio_service: PortfolioServiceDep,
) -> PortfolioDeleteResponse:
    """Удаление портфеля."""
    await portfolio_service.delete(portfolio_id)
    return PortfolioDeleteResponse(portfolio_id=portfolio_id)


@router.post('/{portfolio_id}/assets', status_code=201, responses=responses(400, 404, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при добавлении актива портфеля')
async def add_asset_to_portfolio(
    request: Request,
    portfolio_id: int,
    data: PortfolioAssetCreateRequest,
    portfolio_service: PortfolioServiceDep,
) -> PortfolioResponse:
    """Добавление актива в портфель."""
    await portfolio_service.add_asset(portfolio_id, data)
    return await portfolio_service.get_with_assets(portfolio_id)


@router.delete('/{portfolio_id}/assets/{asset_id}', responses=responses(400, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при удалении актива портфеля')
async def delete_asset_from_portfolio(
    request: Request,
    portfolio_id: int,
    asset_id: int,
    portfolio_service: PortfolioServiceDep,
) -> PortfolioResponse:
    """Удаление актива из портфеля."""
    await portfolio_service.add_asset(portfolio_id, asset_id)
    return await portfolio_service.get_with_assets(portfolio_id)


@router.get('/assets/{asset_id}/transactions', responses=responses(404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении транзакций актива')
async def get_asset_transactions(
    request: Request,
    asset_id: int,
    asset_service: PortfolioAssetServiceDep,
) -> list[TransactionResponse]:
    """Получение транзакций актива."""
    return await asset_service.get_transactions(asset_id)


@router.get('/assets/{asset_id}/distribution', responses=responses(404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении информации о распределении актива')
async def get_asset_distribution(
    request: Request,
    asset_id: int,
    asset_service: PortfolioAssetServiceDep,
) -> dict:
    """Получение информации о распределении актива по портфелям."""
    return await asset_service.get_distribution(asset_id)
