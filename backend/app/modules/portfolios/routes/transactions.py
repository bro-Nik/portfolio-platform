from fastapi import APIRouter, Request

from app.common.exceptions import handle_errors
from app.core.rate_limit import limiter

from app.core import settings
from app.modules.portfolios.dependencies import (
    TransactionServiceDep, require_user,
)
from app.modules.portfolios.schemas import (
    TransactionCreateRequest, TransactionResponseWithAssets,
    TransactionUpdateRequest,
)


router = APIRouter(dependencies=[require_user])


@router.post('/transactions', status_code=201)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка создания транзакции')
async def create_transaction(
    request: Request,
    data: TransactionCreateRequest,
    transaction_service: TransactionServiceDep,
) -> TransactionResponseWithAssets:
    t = await transaction_service.create(data)
    return await transaction_service.build_response_with_assets(t)


@router.put('/transactions/{transaction_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка обновления транзакции')
async def update_transaction(
    request: Request,
    transaction_id: int,
    data: TransactionUpdateRequest,
    transaction_service: TransactionServiceDep,
) -> TransactionResponseWithAssets:
    new_t, old_t = await transaction_service.update(transaction_id, data)
    return await transaction_service.build_response_with_assets(new_t, old_t)


@router.delete('/transactions/{transaction_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления транзакции')
async def delete_transaction(
    request: Request,
    transaction_id: int,
    transaction_service: TransactionServiceDep,
) -> TransactionResponseWithAssets:
    t = await transaction_service.delete(transaction_id)
    return await transaction_service.build_response_with_assets(t)
