from typing import Optional

from fastapi import APIRouter
from shared.api import responses
from shared.exceptions import handle_errors

from app.dependencies import ApiProviderServiceDep
from app.schemas import ApiProviderCreate, ApiProviderResponse, ApiProviderUpdate

router = APIRouter(prefix='/providers', tags=['Providers'], responses=responses(401, 429, 500))


@router.get('/')
@handle_errors('Ошибка при получении провайдеров')
async def get_providers(
    ps: ApiProviderServiceDep,
    skip: int = 0,
    limit: Optional[int] = None,
    active_only: bool = False,
) ->list[ApiProviderResponse]:
    """Получить список API провайдеров"""
    return await ps.get_providers(skip=skip, limit=limit, active_only=active_only)


@router.post('/', status_code=201, responses=responses(400, 409))
@handle_errors('Ошибка при создании провайдера')
async def create_provider(
    provider_data: ApiProviderCreate,
    ps: ApiProviderServiceDep,
) -> ApiProviderResponse:
    """Создать новый API провайдер"""
    return await ps.create_provider(provider_data)


@router.put('/{provider_id}', responses=responses(400, 404, 409))
@handle_errors('Ошибка при обновлении провайдера')
async def update_provider(
    provider_id: int,
    provider_data: ApiProviderUpdate,
    ps: ApiProviderServiceDep,
) -> ApiProviderResponse:
    """Обновить API провайдер"""
    return await ps.update_provider(provider_id, provider_data)


@router.get('/{provider_id}', responses=responses(404))
@handle_errors('Ошибка при получении провайдера')
async def get_provider(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> ApiProviderResponse:
    """Получить информацию об API провайдере"""
    return await ps.get_provider(provider_id)


@router.delete('/{provider_id}', status_code=204, responses=responses(400, 404))
@handle_errors('Ошибка при удалении провайдера')
async def delete_provider(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> None:
    """Удалить API провайдер"""
    await ps.delete_provider(provider_id)


@router.post('/{provider_id}/reset-counters', responses=responses(400, 404, 409))
@handle_errors('Ошибка сброса счетчиков провайдера')
async def reset_counters(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> None:
    """Сбросить счетчики API провайдера"""
    await ps.reset_counters(provider_id)


@router.get('/{provider_id}/stats', responses=responses(404))
@handle_errors('Ошибка получения статистики провайдера')
async def get_provider_stats(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> dict:
    """Получить статистику использования API провайдера"""
    return await ps.get_stats(provider_id)


@router.get('/{provider_id}/logs', responses=responses(404))
@handle_errors('Ошибка получения логов провайдера')
async def get_provider_logs(
    ps: ApiProviderServiceDep,
    provider_id: int,
    hours: int = 24,
    limit: int = 100,
):
    """Получить логи запросов API провайдера"""
    return await ps.get_logs(provider_id, hours=hours, limit=limit)


@router.get("/presets/default")
def get_default_presets(
    ps: ApiProviderServiceDep,
):
    """Получить предустановки для cуществующих API провайдеров"""
    return {'presets': ps.get_providers_with_settings()}


@router.get("/services/with/methods")
async def get_providers_with_methods(
    ps: ApiProviderServiceDep,
):
    """Получить список провайдеров с поддерживаемыми методами"""
    return await ps.get_provider_with_methods()
