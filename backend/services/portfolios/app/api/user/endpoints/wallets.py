"""Кошельки пользователя и их активы.

Все эндпоинты требуют валидный access token
"""

from fastapi import APIRouter, Request
from shared.api import responses
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.core import settings
from app.dependencies import CurrentUser, WalletAssetServiceDep, WalletServiceDep
from app.schemas import (
    TransactionResponse,
    WalletCreateRequest,
    WalletDeleteResponse,
    WalletListResponse,
    WalletResponse,
    WalletUpdateRequest,
)

router = APIRouter(prefix='/wallets', tags=['Wallets'], responses=responses(401, 429, 500))


@router.get('/')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении кошельков')
async def get_user_wallets(
    request: Request,
    current_user: CurrentUser,
    wallet_service: WalletServiceDep,
) -> WalletListResponse:
    """Получение всех кошельков пользователя."""
    return await wallet_service.get_many(current_user.id)


@router.get('/{wallet_id}', responses=responses(404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении кошелька')
async def get_user_wallet(
    request: Request,
    wallet_id: int,
    current_user: CurrentUser,
    wallet_service: WalletServiceDep,
) -> WalletResponse:
    """Получение кошелька пользователя."""
    return await wallet_service.get(wallet_id, current_user.id)


@router.post('/', status_code=201, responses=responses(400, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при создании кошелька')
async def create_wallet(
    request: Request,
    data: WalletCreateRequest,
    current_user: CurrentUser,
    wallet_service: WalletServiceDep,
) -> WalletResponse:
    """Создание нового кошелька."""
    return await wallet_service.create(current_user.id, data)


@router.put('/{wallet_id}', responses=responses(400, 404, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при изменении кошелька')
async def update_wallet(
    request: Request,
    wallet_id: int,
    data: WalletUpdateRequest,
    current_user: CurrentUser,
    wallet_service: WalletServiceDep,
) -> WalletResponse:
    """Обновление кошелька."""
    return await wallet_service.update(wallet_id, current_user.id, data)


@router.delete('/{wallet_id}', responses=responses(400, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при удалении кошелька')
async def delete_wallet(
    request: Request,
    wallet_id: int,
    current_user: CurrentUser,
    wallet_service: WalletServiceDep,
) -> WalletDeleteResponse:
    """Удаление кошелька."""
    return await wallet_service.delete(wallet_id, current_user.id)


@router.get('/assets/{asset_id}/transactions', responses=responses(404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении транзакций актива')
async def get_asset_transactions(
    request: Request,
    asset_id: int,
    current_user: CurrentUser,
    asset_service: WalletAssetServiceDep,
) -> list[TransactionResponse]:
    """Получение транзакций актива."""
    return await asset_service.get_transactions(asset_id, current_user.id)


@router.get('/assets/{asset_id}/distribution', responses=responses(404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении информации о распределении актива')
async def get_asset(
    request: Request,
    asset_id: int,
    current_user: CurrentUser,
    asset_service: WalletAssetServiceDep,
) -> dict:
    """Получение информации о распределении актива по портфелям."""
    return await asset_service.get_distribution(asset_id, current_user.id)
