from app.common.exceptions import handle_errors

from app.modules.market.dependencies import ProviderServiceDep
from app.modules.market.schemas import (
    ProviderCreateRequest, ProviderLog, ProviderResponse,
    ProviderStats, ProviderUpdateRequest,
)
from app.modules.market.routes.app_router import AppRouter


providers_router = AppRouter(prefix='/providers', tags=['Admin | ApiProviders'])


@providers_router.get('')
@handle_errors('Ошибка получения провайдеров')
async def get_providers(provider_service: ProviderServiceDep) -> list[ProviderResponse]:
    return await provider_service.get_all_with_details()


@providers_router.get('/{provider_id}')
@handle_errors('Ошибка получения провайдера')
async def get_provider(provider_id: int, provider_service: ProviderServiceDep) -> ProviderResponse:
    return await provider_service.get(provider_id)


@providers_router.post('', status_code=201)
@handle_errors('Ошибка создания провайдера')
async def create_provider(data: ProviderCreateRequest, provider_service: ProviderServiceDep) -> ProviderResponse:
    return await provider_service.create(data)


@providers_router.put('/{provider_id}')
@handle_errors('Ошибка обновления провайдера')
async def update_provider(provider_id: int, data: ProviderUpdateRequest, provider_service: ProviderServiceDep) -> ProviderResponse:
    return await provider_service.update(provider_id, data)


@providers_router.delete('/{provider_id}', status_code=204)
@handle_errors('Ошибка удаления провайдера')
async def delete_provider(provider_id: int, provider_service: ProviderServiceDep) -> None:
    await provider_service.delete(provider_id)


@providers_router.post('/{provider_id}/reset-counters', status_code=204)
@handle_errors('Ошибка сброса счетчиков')
async def reset_counters(provider_id: int, provider_service: ProviderServiceDep) -> None:
    await provider_service.reset_counters(provider_id)


@providers_router.get('/{provider_id}/stats')
@handle_errors('Ошибка получения статистики')
async def get_provider_stats(provider_id: int, provider_service: ProviderServiceDep) -> ProviderStats:
    return await provider_service.get_stats(provider_id)


@providers_router.get('/{provider_id}/logs')
@handle_errors('Ошибка получения логов')
async def get_provider_logs(provider_service: ProviderServiceDep, provider_id: int, hours: int = 24) -> list[ProviderLog]:
    return await provider_service.get_logs(provider_id, hours=hours)


@providers_router.get('/with/settings')
@handle_errors('Ошибка получения настроек провайдеров')
async def get_providers_with_settings(provider_service: ProviderServiceDep) -> list:
    return provider_service.get_all_with_settings()


@providers_router.get('/with/methods')
@handle_errors('Ошибка получения методов провайдеров')
async def get_providers_with_methods(provider_service: ProviderServiceDep) -> list:
    return await provider_service.get_all_with_methods()
