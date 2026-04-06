"""Управление провайдерами внешних API.

Все эндпоинты требуют валидный access token с ролью ADMIN
"""

from app.api.router import AppRouter
from app.dependencies import ProviderServiceDep
from app.schemas import ProviderCreateRequest, ProviderResponse, ProviderUpdateRequest
from shared.api import responses
from shared.exceptions import handle_errors

router = AppRouter(prefix='/providers', tags=['Admin | ApiProviders'])


@router.get('/')
@handle_errors('Ошибка при получении провайдеров')
async def get_providers(
    provider_service: ProviderServiceDep,
) ->list[ProviderResponse]:
    """Получить список API провайдеров."""
    return await provider_service.get_all_with_details()


@router.get('/{provider_id}', responses=responses(404))
@handle_errors('Ошибка при получении провайдера')
async def get_provider(
    provider_id: int,
    provider_service: ProviderServiceDep,
) -> ProviderResponse:
    """Получить информацию об API провайдере."""
    return await provider_service.get(provider_id)


@router.post('/', status_code=201, responses=responses(400, 409))
@handle_errors('Ошибка при создании провайдера')
async def create_provider(
    data: ProviderCreateRequest,
    provider_service: ProviderServiceDep,
) -> ProviderResponse:
    """Создать новый API провайдер."""
    return await provider_service.create(data)


@router.put('/{provider_id}', responses=responses(400, 404, 409))
@handle_errors('Ошибка при обновлении провайдера')
async def update_provider(
    provider_id: int,
    data: ProviderUpdateRequest,
    provider_service: ProviderServiceDep,
) -> ProviderResponse:
    """Обновить API провайдер."""
    return await provider_service.update(provider_id, data)


@router.delete('/{provider_id}', status_code=204, responses=responses(400, 404))
@handle_errors('Ошибка при удалении провайдера')
async def delete_provider(
    provider_id: int,
    provider_service: ProviderServiceDep,
) -> None:
    """Удалить API провайдер."""
    await provider_service.delete(provider_id)


@router.post('/{provider_id}/reset-counters', status_code=204, responses=responses(400, 404, 409))
@handle_errors('Ошибка сброса счетчиков провайдера')
async def reset_counters(
    provider_id: int,
    provider_service: ProviderServiceDep,
) -> None:
    """Сбросить счетчики API провайдера."""
    await provider_service.reset_counters(provider_id)


@router.get('/{provider_id}/stats', responses=responses(404))
@handle_errors('Ошибка получения статистики провайдера')
async def get_provider_stats(
    provider_id: int,
    provider_service: ProviderServiceDep,
) -> dict:
    """Получить статистику использования API провайдера."""
    return await provider_service.get_stats(provider_id)


@router.get('/{provider_id}/logs', responses=responses(404))
@handle_errors('Ошибка получения логов провайдера')
async def get_provider_logs(
    provider_service: ProviderServiceDep,
    provider_id: int,
    hours: int = 24,
) -> list:
    """Получить логи запросов API провайдера."""
    return await provider_service.get_logs(provider_id, hours=hours)


@router.get('/with/settings')
@handle_errors('Ошибка при получении настроек провайдеров')
def get_providers_with_settings(
    provider_service: ProviderServiceDep,
) -> list:
    """Получить предустановки для cуществующих API провайдеров."""
    return provider_service.get_many_with_settings()


@router.get('/with/methods')
@handle_errors('Ошибка при получении методов провайдеров')
async def get_providers_with_methods(
    provider_service: ProviderServiceDep,
) -> list:
    """Получить список провайдеров с поддерживаемыми методами."""
    return await provider_service.get_many_with_methods()
