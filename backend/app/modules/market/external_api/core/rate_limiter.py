import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
import logging
from types import MappingProxyType

from pydantic import BaseModel, Field
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class LimiterConfig(BaseModel):
    key: str = Field(..., min_length=1)
    requests_per_minute: int | None = Field(0, ge=0, le=1000)
    requests_per_hour: int | None = Field(0, ge=0, le=10000)
    requests_per_day: int | None = Field(0, ge=0, le=10000)
    requests_per_month: int | None = Field(0, ge=0, le=100000)

    @property
    def limits(self) -> dict[str, int]:
        return {
            'minute': self.requests_per_minute or 0,
            'hour': self.requests_per_hour or 0,
            'day': self.requests_per_day or 0,
            'month': self.requests_per_month or 0,
        }


class RateLimiter:
    RETRY_INTERVAL = 1

    def __init__(self, redis: Redis, config: LimiterConfig) -> None:
        self.redis = redis
        self.config = config
        self.counter = RateCounter(redis, config)

    @asynccontextmanager
    async def limit(self, max_wait_time: int = 60) -> AsyncIterator:
        if not self.config.limits or all(limit == 0 for limit in self.config.limits.values()):
            yield
            return
        start_time = datetime.now(UTC)
        while True:
            success = await self.counter.increment()
            if success:
                try:
                    yield
                except Exception:
                    logger.exception('Request failed after increment')
                    raise
                return
            logger.warning('Лимит запросов превышен для %s', self.config.key)
            await asyncio.sleep(self.RETRY_INTERVAL)
            if (datetime.now(UTC) - start_time).total_seconds() >= max_wait_time:
                raise TimeoutError(f'Лимит запросов превышен для {self.config.key} после {max_wait_time}с')


class RateCounter:
    PERIODS = MappingProxyType({'minute': 60, 'hour': 3600, 'day': 86400, 'month': 2592000})

    def __init__(self, redis: Redis, config: LimiterConfig) -> None:
        self.redis = redis
        self.config = config
        self._script = self.redis.register_script(self._get_lua_script())

    def _get_lua_script(self) -> str:
        return """
        local keys = KEYS
        local num_periods = #keys
        local limits = {}
        local ttls = {}
        for i = 1, num_periods do
            limits[i] = tonumber(ARGV[i])
            ttls[i] = tonumber(ARGV[num_periods + i])
        end
        for i = 1, num_periods do
            local current = redis.call('GET', keys[i])
            if current and tonumber(current) >= limits[i] then
                return 0
            end
        end
        for i = 1, num_periods do
            local new = redis.call('INCR', keys[i])
            if new == 1 then
                redis.call('EXPIRE', keys[i], ttls[i])
            end
        end
        return 1
        """

    async def increment(self) -> bool:
        if not self.config.limits:
            return True
        periods = list(self.PERIODS.keys())
        keys = [f'counter:{self.config.key}:{period}' for period in periods]
        result = await self._script(keys=keys, args=[self.config.limits[p] for p in periods] + [self.PERIODS[p] for p in periods])
        return result == 1
