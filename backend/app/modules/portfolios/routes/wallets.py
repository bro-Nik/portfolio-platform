from fastapi import Request

from app.common.routing import DishkaRouter

from app.common.exceptions import handle_errors
from app.core.rate_limit import limiter

from app.core import settings
from app.modules.portfolios.dependencies import (
    TransactionReadQueryDep, WalletAssetServiceDep, WalletReadQueryDep,
    WalletServiceDep,
    require_user,
)
from app.modules.portfolios.schemas import (
    TransactionResponse, WalletArchiveRequest, WalletAssetArchiveRequest,
    WalletCreateRequest, WalletListResponse, WalletResponse,
    WalletUpdateRequest,
)


router = DishkaRouter(dependencies=[require_user])


@router.get('/wallets')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения кошельков')
async def get_user_wallets(
    request: Request,
    query: WalletReadQueryDep,
) -> WalletListResponse:
    wallets = await query.get_all_with_assets()
    return WalletListResponse(wallets=wallets)


@router.get('/wallets/{wallet_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения кошелька')
async def get_user_wallet(
    request: Request,
    wallet_id: int,
    query: WalletReadQueryDep,
) -> WalletResponse:
    return await query.get_with_assets(wallet_id)


@router.post('/wallets', status_code=201)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка создания кошелька')
async def create_wallet(
    request: Request,
    data: WalletCreateRequest,
    wallet_service: WalletServiceDep,
    query: WalletReadQueryDep,
) -> WalletResponse:
    wallet = await wallet_service.create(data)
    return await query.get_with_assets(wallet.id)


@router.put('/wallets/{wallet_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка обновления кошелька')
async def update_wallet(
    request: Request,
    wallet_id: int,
    data: WalletUpdateRequest,
    wallet_service: WalletServiceDep,
    query: WalletReadQueryDep,
) -> WalletResponse:
    wallet = await wallet_service.update(wallet_id, data)
    return await query.get_with_assets(wallet.id)


@router.delete('/wallets/{wallet_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления кошелька')
async def delete_wallet(
    request: Request,
    wallet_id: int,
    wallet_service: WalletServiceDep,
) -> None:
    await wallet_service.delete(wallet_id)


@router.patch('/wallets/{wallet_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка изменения статуса кошелька')
async def set_wallet_archived(
    request: Request,
    wallet_id: int,
    data: WalletArchiveRequest,
    wallet_service: WalletServiceDep,
) -> None:
    await wallet_service.set_archived(wallet_id, data.is_archived)


@router.delete('/wallets/{wallet_id}/assets/{asset_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления актива кошелька')
async def delete_wallet_asset(
    request: Request,
    wallet_id: int,
    asset_id: int,
    wallet_service: WalletServiceDep,
) -> None:
    await wallet_service.delete_asset(wallet_id, asset_id)


@router.patch('/wallets/{wallet_id}/assets/{asset_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка изменения статуса актива кошелька')
async def set_wallet_asset_archived(
    request: Request,
    wallet_id: int,
    asset_id: int,
    data: WalletAssetArchiveRequest,
    wallet_service: WalletServiceDep,
) -> None:
    await wallet_service.set_asset_archived(wallet_id, asset_id, data.is_archived)


@router.get('/wallets/{wallet_id}/assets/{asset_id}/transactions')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения транзакций актива кошелька')
async def get_wallet_asset_transactions(
    request: Request,
    wallet_id: int,
    asset_id: int,
    query: TransactionReadQueryDep,
) -> list[TransactionResponse]:
    return await query.get_wallet_asset_transactions(asset_id)


@router.get('/wallets/{wallet_id}/assets/{asset_id}/distribution')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения распределения актива кошелька')
async def get_wallet_asset_distribution(
    request: Request,
    wallet_id: int,
    asset_id: int,
    asset_service: WalletAssetServiceDep,
) -> dict:
    return await asset_service.get_distribution(asset_id)
