import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
import logging
import random
from types import MappingProxyType

from pydantic import BaseModel, Field
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.modules.market.external_api.exceptions import RateLimiterUnavailableError, RateLimitTimeoutError

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
    MAX_BACKOFF = 60

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
        attempt = 0
        while True:
            success, ttl = await self.counter.increment()
            if success:
                try:
                    yield
                except Exception:
                    logger.exception('Request failed after increment')
                    raise
                return

            attempt += 1

            if ttl is not None:
                wait = min(ttl, self.MAX_BACKOFF) + random.uniform(0, 0.5)
            else:
                wait = min(self.RETRY_INTERVAL * (2 ** attempt), self.MAX_BACKOFF) + random.uniform(0, 1)

            if attempt & (attempt + 1) == 0:
                logger.warning(
                    'Лимит запросов превышен для %s, ожидание %.1fс (попытка %d)',
                    self.config.key, wait, attempt,
                )
            else:
                logger.debug(
                    'Лимит запросов превышен для %s, ожидание %.1fс',
                    self.config.key, wait,
                )

            await asyncio.sleep(wait)

            if (datetime.now(UTC) - start_time).total_seconds() >= max_wait_time:
                raise RateLimitTimeoutError(self.config.key, max_wait_time)


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
        local min_ttl = 0
        for i = 1, num_periods do
            local current = redis.call('GET', keys[i])
            if current and tonumber(current) >= limits[i] then
                local remaining = redis.call('TTL', keys[i])
                if remaining < 0 then
                    remaining = ttls[i]
                end
                if min_ttl == 0 or remaining < min_ttl then
                    min_ttl = remaining
                end
            end
        end
        if min_ttl > 0 then
            return -min_ttl
        end
        for i = 1, num_periods do
            local new = redis.call('INCR', keys[i])
            if new == 1 then
                redis.call('EXPIRE', keys[i], ttls[i])
            end
        end
        return 1
        """

    async def increment(self) -> tuple[bool, int | None]:
        if not self.config.limits:
            return True, None
        periods = [p for p in self.PERIODS if self.config.limits.get(p, 0) > 0]
        if not periods:
            return True, None
        keys = [f'counter:{self.config.key}:{period}' for period in periods]
        try:
            result = await self._script(
                keys=keys,
                args=[self.config.limits[p] for p in periods] + [self.PERIODS[p] for p in periods],
            )
        except RedisError as e:
            logger.error(
                'Redis недоступен. Rate limiter для %s отключён, запросы заблокированы: %s',
                self.config.key, e,
            )
            raise RateLimiterUnavailableError(self.config.key, str(e)) from e
        if result == 1:
            return True, None
        return False, -result
