from datetime import UTC, datetime, timedelta

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictError, NotFoundError

from app.modules.market.models import Provider, RequestLog
from app.modules.market.repositories import ProviderRepository, RequestLogRepository
from app.modules.market.schemas import (
    ProviderCreate, ProviderCreateRequest, ProviderResponse,
    ProviderStats, ProviderUpdate, ProviderUpdateRequest,
)


COUNTER_PERIODS = ['minute', 'hour', 'day', 'month']


class ProviderService:
    def __init__(self, session: AsyncSession, redis: Redis, provider_repo: ProviderRepository, log_repo: RequestLogRepository) -> None:
        self.session = session
        self.redis = redis
        self.repo = provider_repo
        self.log_repo = log_repo

    async def get_all(self) -> list[Provider]:
        return await self.repo.get_all()

    async def get_all_with_details(self) -> list[ProviderResponse]:
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
        provider = await self.repo.get(id)
        if not provider:
            raise NotFoundError('API провайдер не найден')
        return provider

    async def get_by_name(self, name: str) -> Provider:
        provider = await self.repo.get_by_name(name)
        if not provider:
            raise NotFoundError('API провайдер не найден')
        return provider

    async def create(self, data: ProviderCreateRequest) -> Provider:
        if await self.repo.exists_by_name(data.name):
            raise ConflictError(f'Провайдер с именем "{data.name}" уже существует')
        provider = await self.repo.create(ProviderCreate(**data.model_dump()).model_dump())
        await self.session.flush()
        return provider

    async def update(self, id: int, data: ProviderUpdateRequest) -> Provider:
        provider = await self.get(id)
        if data.api_key == '***':
            data.api_key = provider.api_key
        return await self.repo.update(id, ProviderUpdate(**data.model_dump()).model_dump())

    async def delete(self, id: int) -> None:
        await self.repo.delete(id)

    async def reset_counters(self, id: int) -> None:
        provider = await self.get(id)
        async for key in self.redis.scan_iter(match=f'counter:{provider.name}:*'):
            await self.redis.delete(key)

    async def get_stats(self, id: int) -> ProviderStats:
        provider = await self.get(id)
        day_ago = datetime.now(UTC) - timedelta(days=1)
        logs = await self.log_repo.get_stats_by_provider(id, day_ago)
        counters = await self.get_current_counters(provider.name)

        minute_limit = provider.requests_per_minute or 0
        hour_limit = provider.requests_per_hour or 0
        day_limit = provider.requests_per_day or 0
        month_limit = provider.requests_per_month or 0

        utilization = {}
        if minute_limit:
            utilization['minute'] = round(counters.get('minute', 0) / minute_limit * 100, 1)
        if hour_limit:
            utilization['hour'] = round(counters.get('hour', 0) / hour_limit * 100, 1)
        if day_limit:
            utilization['day'] = round(counters.get('day', 0) / day_limit * 100, 1)
        if month_limit:
            utilization['month'] = round(counters.get('month', 0) / month_limit * 100, 1)

        return ProviderStats(
            provider_name=provider.name,
            requests_today=logs.total or 0, successful_today=logs.successful or 0,
            failed_today=(logs.total or 0) - (logs.successful or 0),
            avg_response_time=logs.avg_response_time,
            minute_counter=counters.get('minute', 0), minute_limit=minute_limit,
            hour_counter=counters.get('hour', 0), hour_limit=hour_limit,
            day_counter=counters.get('day', 0), day_limit=day_limit,
            month_counter=counters.get('month', 0), month_limit=month_limit,
            utilization_percent=utilization,
        )

    async def get_logs(self, provider_id: int, hours: int = 24) -> list[RequestLog]:
        await self.get(provider_id)
        last_time = datetime.now(UTC) - timedelta(hours=hours)
        return await self.log_repo.get_all_by_provider(provider_id, last_time)

    async def get_all_with_settings(self) -> list:
        from app.modules.market.external_api.core import registry
        return [{'name': name, 'description': cls.DESCRIPTION, 'limits': {
            'per_minute': cls.REQUESTS_PER_MINUTE, 'per_hour': cls.REQUESTS_PER_HOUR,
            'per_day': cls.REQUESTS_PER_DAY, 'per_month': cls.REQUESTS_PER_MONTH,
        }} for name, cls in registry.PROVIDERS.items()]

    async def get_all_with_methods(self) -> list[dict]:
        from app.modules.market.external_api.core import registry
        return [{'provider': name, 'methods': registry.get_provider_methods(name)} for name in registry.PROVIDERS]

    async def get_current_counter(self, name: str, period: str) -> int:
        key = f'counter:{name}:{period}'
        value = await self.redis.get(key)
        return int(value) if value else 0

    async def get_current_counters(self, name: str) -> dict[str, int]:
        keys = [f'counter:{name}:{period}' for period in COUNTER_PERIODS]
        values = await self.redis.mget(keys)
        return {period: int(v) if v else 0 for period, v in zip(COUNTER_PERIODS, values, strict=False)}

    async def _get_counters_for_providers(self, providers: list[Provider]) -> dict[str, dict[str, int]]:
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
            name, period = key_to_info[key]
            result[name][period] = int(value) if value else 0
        return result
