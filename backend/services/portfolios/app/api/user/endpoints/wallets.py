"""Кошельки пользователя и их активы.

Все эндпоинты требуют валидный access token
"""

from fastapi import APIRouter, Request

from shared.api import responses
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.core import settings
from app.dependencies import WalletAssetServiceDep, WalletServiceDep
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
    wallet_service: WalletServiceDep,
) -> WalletListResponse:
    """Получение всех кошельков пользователя."""
    wallets = await wallet_service.get_all_with_assets()
    return WalletListResponse(wallets=wallets)


@router.get('/{wallet_id}', responses=responses(404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении кошелька')
async def get_user_wallet(
    request: Request,
    wallet_id: int,
    wallet_service: WalletServiceDep,
) -> WalletResponse:
    """Получение кошелька пользователя."""
    return await wallet_service.get_with_assets(wallet_id)


@router.post('/', status_code=201, responses=responses(400, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при создании кошелька')
async def create_wallet(
    request: Request,
    data: WalletCreateRequest,
    wallet_service: WalletServiceDep,
) -> WalletResponse:
    """Создание нового кошелька."""
    wallet = await wallet_service.create(data)
    return await wallet_service.get_with_assets(wallet.id)


@router.put('/{wallet_id}', responses=responses(400, 404, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при изменении кошелька')
async def update_wallet(
    request: Request,
    wallet_id: int,
    data: WalletUpdateRequest,
    wallet_service: WalletServiceDep,
) -> WalletResponse:
    """Обновление кошелька."""
    wallet = await wallet_service.update(wallet_id, data)
    return await wallet_service.get_with_assets(wallet.id)


@router.delete('/{wallet_id}', responses=responses(400, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при удалении кошелька')
async def delete_wallet(
    request: Request,
    wallet_id: int,
    wallet_service: WalletServiceDep,
) -> WalletDeleteResponse:
    """Удаление кошелька."""
    await wallet_service.delete(wallet_id)
    return WalletDeleteResponse(wallet_id=wallet_id)


@router.get('/assets/{asset_id}/transactions', responses=responses(404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении транзакций актива')
async def get_asset_transactions(
    request: Request,
    asset_id: int,
    asset_service: WalletAssetServiceDep,
) -> list[TransactionResponse]:
    """Получение транзакций актива."""
    return await asset_service.get_transactions(asset_id)


@router.get('/assets/{asset_id}/distribution', responses=responses(404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении информации о распределении актива')
async def get_asset(
    request: Request,
    asset_id: int,
    asset_service: WalletAssetServiceDep,
) -> dict:
    """Получение информации о распределении актива по портфелям."""
    return await asset_service.get_distribution(asset_id)
