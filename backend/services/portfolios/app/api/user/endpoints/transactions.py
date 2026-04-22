"""Транзакции в активах портфелей и кошельков пользователя.

Все эндпоинты требуют валидный access token
"""

from fastapi import APIRouter, Request

from shared.api import responses
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.core import settings
from app.dependencies import TransactionServiceDep
from app.schemas import TransactionCreateRequest, TransactionResponseWithAssets
from app.schemas.transaction import TransactionUpdateRequest

router = APIRouter(prefix='/transactions', tags=['Transactions'], responses=responses(401, 429, 500))


@router.post('/', status_code=201, responses=responses(400, 404, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при создании транзакции')
async def create_transaction(
    request: Request,
    data: TransactionCreateRequest,
    transaction_service: TransactionServiceDep,
) -> TransactionResponseWithAssets:
    """Создание новой транзакции."""
    transaction = await transaction_service.create(data)
    return await transaction_service.build_response_with_assets(transaction)


@router.put('/{transaction_id}', responses=responses(400, 404, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при изменении транзакции')
async def update_transaction(
    request: Request,
    transaction_id: int,
    data: TransactionUpdateRequest,
    transaction_service: TransactionServiceDep,
) -> TransactionResponseWithAssets:
    """Изменение транзакции."""
    print(f"Updating transaction {transaction_id} with data: {data}")  # 👈
    result = await transaction_service.update(transaction_id, data)
    print(f"Result: {result}")  # 👈
    # return result
    return await transaction_service.build_response_with_assets(result)
    new_transaction, transaction = await transaction_service.update(transaction_id, data)
    return await transaction_service.build_response_with_assets(new_transaction, transaction)


@router.delete('/{transaction_id}', responses=responses(400, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при удалении транзакции')
async def delete_transaction(
    request: Request,
    transaction_id: int,
    transaction_service: TransactionServiceDep,
) -> TransactionResponseWithAssets:
    """Удаление транзакции."""
    transaction = await transaction_service.delete(transaction_id)
    return await transaction_service.build_response_with_assets(transaction)
