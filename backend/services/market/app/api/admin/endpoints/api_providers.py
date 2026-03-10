from typing import List, Optional

from fastapi import APIRouter
from shared.exceptions import handle_errors

from app import schemas
from app.dependencies import ApiProviderServiceDep

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("/", response_model=List[schemas.ApiProviderResponse])
@handle_errors('Ошибка при получении провайдеров')
async def get_providers(
    ps: ApiProviderServiceDep,
    skip: int = 0,
    limit: Optional[int] = None,
    active_only: bool = False,
) ->List[schemas.ApiProviderResponse]:
    """Получить список API провайдеров"""
    return await ps.get_providers(skip=skip, limit=limit, active_only=active_only)


@router.post("/", response_model=schemas.ApiProviderResponse)
@handle_errors('Ошибка при создании провайдера')
async def create_provider(
    provider_data: schemas.ApiProviderCreate,
    ps: ApiProviderServiceDep,
) -> schemas.ApiProviderResponse:
    """Создать новый API провайдер"""
    return await ps.create_provider(provider_data)


@router.put("/{provider_id}", response_model=schemas.ApiProviderResponse)
@handle_errors('Ошибка при обновлении провайдера')
async def update_provider(
    provider_id: int,
    provider_data: schemas.ApiProviderUpdate,
    ps: ApiProviderServiceDep,
) -> schemas.ApiProviderResponse:
    """Обновить API провайдер"""
    return await ps.update_provider(provider_id, provider_data)


@router.get("/{provider_id}", response_model=schemas.ApiProviderResponse)
@handle_errors('Ошибка при получении провайдера')
async def get_provider(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> schemas.ApiProviderResponse:
    """Получить информацию об API провайдере"""
    return await ps.get_provider(provider_id)


@router.delete("/{provider_id}")
@handle_errors('Ошибка при удалении провайдера')
async def delete_provider(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> dict:
    """Удалить API провайдер"""
    await ps.delete_provider(provider_id)
    return {"message": "API провайдер удален"}


@router.post("/{provider_id}/reset-counters")
@handle_errors('Ошибка сброса счетчиков провайдера')
async def reset_counters(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> dict:
    """Сбросить счетчики API провайдера"""
    await ps.reset_counters(provider_id)
    return {"message": "Счетчики сброшены"}


@router.get("/{provider_id}/stats")
@handle_errors('Ошибка получения статистики провайдера')
async def get_provider_stats(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> dict:
    """Получить статистику использования API провайдера"""
    return await ps.get_stats(provider_id)


@router.get("/{provider_id}/logs")
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
async def get_provider_with_methods(
    ps: ApiProviderServiceDep,
):
    """Получить список провайдеров с поддерживаемыми методами"""
    return await ps.get_provider_with_methods()
