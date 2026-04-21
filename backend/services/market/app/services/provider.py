from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Provider, RequestLog
from app.schemas import (
    ProviderCreate,
    ProviderCreateRequest,
    ProviderResponse,
    ProviderStats,
    ProviderUpdate,
    ProviderUpdateRequest,
)
from shared.exceptions import ConflictError, NotFoundError

if TYPE_CHECKING:
    from app.repositories import ProviderRepository, RequestLogRepository

COUNTER_PERIODS = ['minute', 'hour', 'day', 'month']


class ProviderService:
    """Сервис для работы с API провайдерами."""

    def __init__(
        self,
        session: AsyncSession,
        redis: Redis,
        provider_repo: 'ProviderRepository',
        log_repo: 'RequestLogRepository',
    ) -> None:
        self.session = session
        self.redis = redis
        self.repo = provider_repo
        self.log_repo = log_repo

    async def get_all(self) -> list[Provider]:
        """Получить список провайдеров."""
        return await self.repo.get_all()

    async def get_all_with_details(self) -> list[ProviderResponse]:
        """Получить список провайдеров."""
        providers = await self.get_all()
        counters_map = await self._get_counters_for_providers(providers)

        result = []
        for provider in providers:
            counters = counters_map.get(provider.name, {})
            p = ProviderResponse.model_validate(provider)
            p.minute_counter = counters.get('minute', 0)
            p.hour_counter = counters.get('hour', 0)
            p.day_counter = counters.get('day', 0)
            p.month_counter = counters.get('month', 0)
            result.append(p)

        return result

    async def get(self, id: int) -> Provider:
        """Получить провайдера по ID."""
        provider = await self.repo.get(id)
        self._verify(provider)
        return provider

    async def get_by_name(self, name: str) -> Provider:
        """Получить провайдера по названию."""
        provider = await self.repo.get_by_name(name)
        self._verify(provider)
        return provider

    async def create(self, data: ProviderCreateRequest) -> Provider:
        """Создать провайдера."""
        await self._validate_create_data(data)

        data_to_db = ProviderCreate(**data.model_dump())
        provider = await self.repo.create(data_to_db)
        await self.session.flush()
        return provider

    async def update(self, id: int, data: ProviderUpdateRequest) -> Provider:
        """Обновить провайдера."""
        provider = await self.get(id)

        if data.api_key == '***':
            data.api_key = provider.api_key

        await self._validate_update_data(data, provider)

        data_to_db = ProviderUpdate(**data.model_dump())
        return await self.repo.update(id, data_to_db)

    async def delete(self, id: int) -> None:
        """Удалить провайдера."""
        provider = await self.get(id)
        await self.session.refresh(provider, ['tasks'])
        await self.repo.delete(id)

    async def reset_counters(self, id: int) -> None:
        """Сбросить счетчики провайдера."""
        provider = await self.get(id)

        async for key in self.redis.scan_iter(match=f'counter:{provider.name}:*'):
            await self.redis.delete(key)

    async def get_stats(self, id: int) -> ProviderStats:
        """Получить статистику по провайдеру."""
        provider = await self.get(id)

        # Запросы за последние 24 часа
        day_ago = datetime.now(UTC) - timedelta(days=1)
        logs = await self.log_repo.get_stats_by_provider(id, day_ago)

        counters = await self.get_current_counters(provider.name)
        minute_counter = counters.get('minute', 0)
        hour_counter = counters.get('hour', 0)
        day_counter = counters.get('day', 0)
        month_counter = counters.get('month', 0)

        # Расчет процентов использования
        p = provider
        min_percent = (minute_counter / p.requests_per_minute * 100) if p.requests_per_minute else 0
        hour_percent = (hour_counter / p.requests_per_hour * 100) if p.requests_per_hour else 0
        day_percent = (day_counter / p.requests_per_day * 100) if p.requests_per_day else 0

        return ProviderStats(
            provider_name=provider.name,
            requests_today=logs.total or 0,
            successful_today=logs.successful or 0,
            failed_today=(logs.total or 0) - (logs.successful or 0),
            avg_response_time=round(logs.avg_response_time or 0, 2),
            minute_limit=provider.requests_per_minute or 0,
            hour_limit=provider.requests_per_hour or 0,
            day_limit=provider.requests_per_day or 0,
            month_limit=provider.requests_per_month or 0,
            minute_counter=minute_counter,
            hour_counter=hour_counter,
            day_counter=day_counter,
            month_counter=month_counter,
            utilization_percent = {
                'minute': round(min_percent, 2),
                'hour': round(hour_percent, 2),
                'day': round(day_percent, 2),
            },
        )

    async def get_logs(self, id: int, hours: int = 24) -> list[RequestLog]:
        """Получить логи провайдера."""
        last_time = datetime.now(UTC) - timedelta(hours=hours)
        return await self.log_repo.get_many_by_provider(id, last_time)

    async def get_many_with_methods(self) -> list[dict[str, Any]]:
        """Получить провайдеров с доступными методами."""
        from app.external_api.core.registry import ProviderRegistry
        result = []
        providers = await self.repo.get_all_active()
        for provider in providers:
            methods = list(ProviderRegistry.get_provider_methods(provider.name))
            if methods:
                result.append({
                    'id': provider.id,
                    'name': provider.name,
                    'methods': methods,
                })
        return result

    def get_many_with_settings(self) -> list[dict[str, Any]]:
        """Получить провайдеров с настройками."""
        from app.external_api.core.registry import ProviderRegistry
        result = []
        providers = ProviderRegistry.PROVIDERS
        for provider_name in providers:
            provider = providers[provider_name]
            provider_dict = {
                'name': provider_name,
                'description': provider.DESCRIPTION,
                'requests_per_minute': provider.REQUESTS_PER_MINUTE,
                'requests_per_hour': provider.REQUESTS_PER_HOUR,
                'requests_per_day': provider.REQUESTS_PER_DAY,
                'requests_per_month': provider.REQUESTS_PER_MONTH,
                'timeout': provider.TIMEOUT,
            }
            result.append(provider_dict)

        return result

    def _verify(self, provider: Provider) -> None:
        if not provider:
            raise NotFoundError('API провайдер не найден')

    async def _validate_create_data(self, data: ProviderCreateRequest) -> None:
        await self._validate_unique_name(data.name)

    async def _validate_update_data(self, data: ProviderUpdateRequest, provider: Provider) -> None:
        pass

    async def _validate_unique_name(self, name: str) -> None:
        if await self.repo.exists_by_name(name):
            raise ConflictError(f'Провайдер с именем "{name}" уже существует')

    async def get_current_counter(self, name: str, period: str) -> int:
        """Получить текущее значение счетчика."""
        key = f'counter:{name}:{period}'
        value = await self.redis.get(key)
        return int(value) if value else 0

    async def get_current_counters(self, name: str) -> dict[str, int]:
        """Получить все текущие счетчики."""
        keys = [f'counter:{name}:{period}' for period in COUNTER_PERIODS]
        values = await self.redis.mget(keys)
        return {period: int(value) if value else 0
                for period, value in zip(COUNTER_PERIODS, values, strict=False)}

    async def _get_counters_for_providers(self, providers: list[Provider]) -> dict[str, dict[str, int]]:
        """Получить счетчики для нескольких провайдеров одним запросом."""
        if not providers:
            return {}

        result = {p.name: {} for p in providers}

        keys = []
        key_to_info = {}

        for provider in providers:
            for period in COUNTER_PERIODS:
                key = f'counter:{provider.name}:{period}'
                keys.append(key)
                key_to_info[key] = (provider.name, period)

        values = await self.redis.mget(keys)

        for key, value in zip(keys, values, strict=False):
            provider_name, period = key_to_info[key]
            result[provider_name][period] = int(value) if value else 0

        return result
