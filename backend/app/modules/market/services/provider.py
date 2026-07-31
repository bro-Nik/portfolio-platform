from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BusinessRuleError, ConflictError, NotFoundError

from app.modules.market.external_api.core import registry
from app.modules.market.models import Provider, RequestLog
from app.modules.market.repositories import ProviderRepository, RequestLogRepository
from app.modules.market.schemas import (
    ProviderCreate, ProviderCreateRequest, ProviderResponse,
    ProviderStats, ProviderUpdate, ProviderUpdateRequest,
)


COUNTER_PERIODS = ['minute', 'hour', 'day', 'month']


@dataclass
class ProviderConfig:
    name: str
    requests_per_minute: int | None
    requests_per_hour: int | None
    requests_per_day: int | None
    requests_per_month: int | None
    timeout: int
    retry_delay: int
    api_key: str | None


class ProviderService:
    def __init__(self, session: AsyncSession, redis: Redis, provider_repo: ProviderRepository, log_repo: RequestLogRepository) -> None:
        self.session = session
        self.redis = redis
        self.repo = provider_repo
        self.log_repo = log_repo

    async def get_all_with_details(self) -> list[dict]:
        db_providers = await self.repo.get_all()
        db_map = {p.name: p for p in db_providers}
        counters_map = await self._get_counters_for_providers(
            list(registry.PROVIDERS.keys())
        )

        result = []
        for name, cls in registry.PROVIDERS.items():
            db = db_map.get(name)
            methods = registry.get_provider_methods(name)
            counters = counters_map.get(name, {})

            result.append({
                'id': db.id if db else None,
                'name': name,
                'description': cls.DESCRIPTION,
                'has_config': db is not None,
                'supported_markets': db.supported_markets if db and db.supported_markets else cls.SUPPORTED_MARKETS,
                'api_key_required': cls.API_KEY_REQUIRED,
                'api_key': db.api_key if db else None,
                'requests_per_minute': db.requests_per_minute if db and db.requests_per_minute is not None else cls.REQUESTS_PER_MINUTE,
                'requests_per_hour': db.requests_per_hour if db and db.requests_per_hour is not None else cls.REQUESTS_PER_HOUR,
                'requests_per_day': db.requests_per_day if db and db.requests_per_day is not None else cls.REQUESTS_PER_DAY,
                'requests_per_month': db.requests_per_month if db and db.requests_per_month is not None else cls.REQUESTS_PER_MONTH,
                'retry_delay': db.retry_delay if db else cls.RETRY_DELAY if hasattr(cls, 'RETRY_DELAY') else 60,
                'timeout': db.timeout if db else cls.TIMEOUT,
                'is_active': db.is_active if db else False,
                'minute_counter': counters.get('minute', 0),
                'hour_counter': counters.get('hour', 0),
                'day_counter': counters.get('day', 0),
                'month_counter': counters.get('month', 0),
                'methods': methods,
            })
        return result

    async def get_config_by_name(self, name: str) -> ProviderConfig:
        cls = registry.PROVIDERS.get(name)
        if not cls:
            raise NotFoundError(f'API провайдер {name} не зарегистрирован')

        db = await self.repo.get_by_name(name)
        return ProviderConfig(
            name=name,
            requests_per_minute=db.requests_per_minute if db and db.requests_per_minute is not None else cls.REQUESTS_PER_MINUTE,
            requests_per_hour=db.requests_per_hour if db and db.requests_per_hour is not None else cls.REQUESTS_PER_HOUR,
            requests_per_day=db.requests_per_day if db and db.requests_per_day is not None else cls.REQUESTS_PER_DAY,
            requests_per_month=db.requests_per_month if db and db.requests_per_month is not None else cls.REQUESTS_PER_MONTH,
            timeout=db.timeout if db else cls.TIMEOUT,
            retry_delay=db.retry_delay if db else 60,
            api_key=db.api_key if db else None,
        )

    async def get_db_record(self, name: str) -> Provider:
        provider = await self.repo.get_by_name(name)
        if not provider:
            raise NotFoundError(f'API провайдер {name} не найден')
        return provider

    async def _validate_can_be_active(self, name: str, api_key: str | None) -> None:
        cls = registry.PROVIDERS.get(name)
        if not cls:
            raise NotFoundError(f'API провайдер {name} не зарегистрирован')
        issues = cls.validate_config(api_key)
        if issues:
            raise BusinessRuleError(f'Провайдер "{name}" не может быть активирован: {"; ".join(issues)}')

    async def create(self, data: ProviderCreateRequest) -> Provider:
        if await self.repo.exists_by_name(data.name):
            raise ConflictError(f'Провайдер с именем "{data.name}" уже существует')
        if data.is_active:
            await self._validate_can_be_active(data.name, data.api_key)
        provider = await self.repo.create(ProviderCreate(**data.model_dump()).model_dump())
        await self.session.commit()
        return provider

    async def update(self, name: str, data: ProviderUpdateRequest) -> Provider:
        provider = await self.get_db_record(name)
        if data.api_key == '***':
            data.api_key = provider.api_key
        if data.is_active:
            await self._validate_can_be_active(name, data.api_key)
        updated = await self.repo.update(provider.id, ProviderUpdate(**data.model_dump()).model_dump())
        await self.session.commit()
        return updated

    async def delete(self, name: str) -> None:
        provider = await self.get_db_record(name)
        await self.repo.delete(provider.id)
        await self.session.commit()

    async def reset_counters(self, name: str) -> None:
        async for key in self.redis.scan_iter(match=f'counter:{name}:*'):
            await self.redis.delete(key)

    async def get_stats(self, name: str) -> ProviderStats:
        config = await self.get_config_by_name(name)
        db = await self.repo.get_by_name(name)
        day_ago = datetime.now(UTC) - timedelta(days=1)

        if db:
            logs = await self.log_repo.get_stats_by_provider(name, day_ago)
        else:
            logs = type('Stats', (), {'total': 0, 'successful': 0, 'avg_response_time': None})()

        counters = await self.get_current_counters(name)

        def _limit(val):
            return val or 0

        utilization = {}
        if config.requests_per_minute:
            utilization['minute'] = round(counters.get('minute', 0) / config.requests_per_minute * 100, 1)
        if config.requests_per_hour:
            utilization['hour'] = round(counters.get('hour', 0) / config.requests_per_hour * 100, 1)
        if config.requests_per_day:
            utilization['day'] = round(counters.get('day', 0) / config.requests_per_day * 100, 1)
        if config.requests_per_month:
            utilization['month'] = round(counters.get('month', 0) / config.requests_per_month * 100, 1)

        return ProviderStats(
            provider_name=name,
            requests_today=logs.total or 0, successful_today=logs.successful or 0,
            failed_today=(logs.total or 0) - (logs.successful or 0),
            avg_response_time=logs.avg_response_time,
            minute_counter=counters.get('minute', 0), minute_limit=_limit(config.requests_per_minute),
            hour_counter=counters.get('hour', 0), hour_limit=_limit(config.requests_per_hour),
            day_counter=counters.get('day', 0), day_limit=_limit(config.requests_per_day),
            month_counter=counters.get('month', 0), month_limit=_limit(config.requests_per_month),
            utilization_percent=utilization,
        )

    async def get_logs(self, name: str, hours: int = 24) -> list[RequestLog]:
        last_time = datetime.now(UTC) - timedelta(hours=hours)
        return await self.log_repo.get_all_by_provider(name, last_time)

    async def get_all_with_settings(self) -> list[dict]:
        return [{'name': name, 'description': cls.DESCRIPTION, 'limits': {
            'per_minute': cls.REQUESTS_PER_MINUTE, 'per_hour': cls.REQUESTS_PER_HOUR,
            'per_day': cls.REQUESTS_PER_DAY, 'per_month': cls.REQUESTS_PER_MONTH,
        }} for name, cls in registry.PROVIDERS.items()]

    async def get_all_with_methods(self) -> list[dict]:
        db_providers = await self.repo.get_all()
        db_map = {p.name: p for p in db_providers}
        result = []
        for name, cls in registry.PROVIDERS.items():
            db = db_map.get(name)
            result.append({
                'name': name,
                'supported_markets': db.supported_markets if db and db.supported_markets else cls.SUPPORTED_MARKETS,
                'api_key': db.api_key if db else None,
                'api_key_required': cls.API_KEY_REQUIRED,
                'requests_per_minute': db.requests_per_minute if db and db.requests_per_minute is not None else cls.REQUESTS_PER_MINUTE,
                'requests_per_hour': db.requests_per_hour if db and db.requests_per_hour is not None else cls.REQUESTS_PER_HOUR,
                'requests_per_day': db.requests_per_day if db and db.requests_per_day is not None else cls.REQUESTS_PER_DAY,
                'requests_per_month': db.requests_per_month if db and db.requests_per_month is not None else cls.REQUESTS_PER_MONTH,
                'timeout': db.timeout if db else cls.TIMEOUT,
                'is_active': db.is_active if db else False,
                'methods': registry.get_provider_methods(name),
            })
        return result

    async def get_current_counter(self, name: str, period: str) -> int:
        key = f'counter:{name}:{period}'
        value = await self.redis.get(key)
        return int(value) if value else 0

    async def get_current_counters(self, name: str) -> dict[str, int]:
        keys = [f'counter:{name}:{period}' for period in COUNTER_PERIODS]
        values = await self.redis.mget(keys)
        return {period: int(v) if v else 0 for period, v in zip(COUNTER_PERIODS, values, strict=False)}

    async def _get_counters_for_providers(self, names: list[str]) -> dict[str, dict[str, int]]:
        if not names:
            return {}
        keys = []
        key_to_info = {}
        for name in names:
            for period in COUNTER_PERIODS:
                key = f'counter:{name}:{period}'
                keys.append(key)
                key_to_info[key] = (name, period)
        values = await self.redis.mget(keys)
        result = {name: {} for name in names}
        for key, value in zip(keys, values, strict=False):
            name, period = key_to_info[key]
            result[name][period] = int(value) if value else 0
        return result
