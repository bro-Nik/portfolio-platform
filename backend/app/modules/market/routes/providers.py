from fastapi import Request

from app.common.exceptions import handle_errors
from app.core import settings
from app.core.rate_limit import limiter
from app.modules.market.dependencies import ProviderServiceDep
from app.modules.market.routes.app_router import AppRouter
from app.modules.market.schemas import (
    ProviderCreateRequest,
    ProviderLog,
    ProviderResponse,
    ProviderStats,
    ProviderUpdateRequest,
)

providers_router = AppRouter(prefix='/providers', tags=['Admin | ApiProviders'])


@providers_router.get('/with/settings')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения настроек провайдеров')
async def get_providers_with_settings(
    request: Request,
    provider_service: ProviderServiceDep,
) -> list:
    return await provider_service.get_all_with_settings()


@providers_router.get('/with/methods')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения методов провайдеров')
async def get_providers_with_methods(
    request: Request,
    provider_service: ProviderServiceDep,
) -> list:
    return await provider_service.get_all_with_methods()


@providers_router.get('')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения провайдеров')
async def get_providers(
    request: Request,
    provider_service: ProviderServiceDep,
) -> list:
    return await provider_service.get_all_with_details()


@providers_router.get('/{provider_name}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения провайдера')
async def get_provider(
    request: Request,
    provider_name: str,
    provider_service: ProviderServiceDep,
) -> ProviderResponse:
    return await provider_service.get_db_record(provider_name)


@providers_router.post('', status_code=201)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка создания провайдера')
async def create_provider(
    request: Request,
    data: ProviderCreateRequest,
    provider_service: ProviderServiceDep,
) -> ProviderResponse:
    return await provider_service.create(data)


@providers_router.put('/{provider_name}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка обновления провайдера')
async def update_provider(
    request: Request,
    provider_name: str,
    data: ProviderUpdateRequest,
    provider_service: ProviderServiceDep,
) -> ProviderResponse:
    return await provider_service.update(provider_name, data)


@providers_router.delete('/{provider_name}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления провайдера')
async def delete_provider(
    request: Request,
    provider_name: str,
    provider_service: ProviderServiceDep,
) -> None:
    await provider_service.delete(provider_name)


@providers_router.post('/{provider_name}/reset-counters', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка сброса счетчиков')
async def reset_counters(
    request: Request,
    provider_name: str,
    provider_service: ProviderServiceDep,
) -> None:
    await provider_service.reset_counters(provider_name)


@providers_router.get('/{provider_name}/stats')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения статистики')
async def get_provider_stats(
    request: Request,
    provider_name: str,
    provider_service: ProviderServiceDep,
) -> ProviderStats:
    return await provider_service.get_stats(provider_name)


@providers_router.get('/{provider_name}/logs')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения логов')
async def get_provider_logs(
    request: Request,
    provider_service: ProviderServiceDep,
    provider_name: str,
    hours: int = 24,
) -> list[ProviderLog]:
    return await provider_service.get_logs(provider_name, hours=hours)
