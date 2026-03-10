from typing import List, Optional

from fastapi import APIRouter, HTTPException

from app import schemas
from app.dependencies import ApiProviderServiceDep

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("/", response_model=List[schemas.ApiProviderResponse])
async def get_providers(
    ps: ApiProviderServiceDep,
    skip: int = 0,
    limit: Optional[int] = None,
    active_only: bool = False,
) ->List[schemas.ApiProviderResponse]:
    """Получить список API провайдеров"""
    try:
        providers = await ps.get_providers(skip=skip, limit=limit, active_only=active_only)
        return providers
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=schemas.ApiProviderResponse)
async def create_provider(
    provider_data: schemas.ApiProviderCreate,
    ps: ApiProviderServiceDep,
) -> schemas.ApiProviderResponse:
    """Создать новый API провайдер"""
    try:
        provider = await ps.create_provider(provider_data)
        return provider
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{provider_id}", response_model=schemas.ApiProviderResponse)
async def update_provider(
    provider_id: int,
    provider_data: schemas.ApiProviderUpdate,
    ps: ApiProviderServiceDep,
) -> schemas.ApiProviderResponse:
    """Обновить API провайдер"""
    try:
        provider = await ps.update_provider(provider_id, provider_data)
        if not provider:
            raise HTTPException(status_code=404, detail="API провайдер не найден")
        return provider
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{provider_id}", response_model=schemas.ApiProviderResponse)
async def get_provider(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> schemas.ApiProviderResponse:
    """Получить информацию об API провайдере"""
    try:
        provider = await ps.get_provider(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="API провайдер не найден")
        return provider
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> dict:
    """Удалить API провайдер"""
    try:
        await ps.delete_provider(provider_id)
        return {"message": "API провайдер удален"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{provider_id}/reset-counters")
async def reset_counters(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> dict:
    """Сбросить счетчики API провайдера"""
    try:
        provider = await ps.reset_counters(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail="API провайдер не найден")
        return {"message": "Счетчики сброшены"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{provider_id}/stats")
async def get_provider_stats(
    provider_id: int,
    ps: ApiProviderServiceDep,
) -> dict:
    """Получить статистику использования API провайдера"""
    try:
        stats = await ps.get_stats(provider_id)
        if not stats:
            raise HTTPException(status_code=404, detail="API провайдер не найден")
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{provider_id}/logs")
async def get_provider_logs(
    ps: ApiProviderServiceDep,
    provider_id: int,
    hours: int = 24,
    limit: int = 100,
):
    """Получить логи запросов API провайдера"""
    try:
        logs = await ps.get_logs(provider_id, hours=hours, limit=limit)
        return logs
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
