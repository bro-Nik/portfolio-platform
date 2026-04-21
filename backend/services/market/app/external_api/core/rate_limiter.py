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
    """Rate limiter с проверкой лимитов для всех периодов.

    Поддерживает лимиты на минуту, час, день и месяц.
    При превышении лимита ожидает и повторяет попытки до max_wait_time.
    """

    RETRY_INTERVAL = 1  # секунд

    def __init__(self, redis: Redis, config: LimiterConfig) -> None:
        self.redis = redis
        self.config = config
        self.counter = RateCounter(redis, config)

    @asynccontextmanager
    async def limit(self, max_wait_time: int = 30) -> AsyncIterator:
        """Проверить все лимиты и выполнить запрос."""
        if not self.config.limits or all(limit == 0 for limit in self.config.limits.values()):
            logger.debug('Нет лимитов для %s', self.config.key)
            yield
            return

        start_time = datetime.now(UTC)

        while True:
            success = await self.counter.increment()

            if success:
                logger.debug('Запрос разрешен для %s', self.config.key)
                try:
                    yield
                except Exception:
                    logger.exception('Запрос не выполнен после увеличения')
                    raise
                return

            # Лимит превышен
            logger.warning('Превышен лимит запросов для %s', self.config.key)

            await asyncio.sleep(self.RETRY_INTERVAL)

            elapsed = (datetime.now(UTC) - start_time).total_seconds()
            if elapsed >= max_wait_time:
                raise TimeoutError(f'Rate limit timeout for {self.config.key} after {max_wait_time}s')


class RateCounter:
    """Счетчики запросов."""

    # Периоды и их TTL в секундах
    PERIODS = MappingProxyType({'minute': 60, 'hour': 3600, 'day': 86400, 'month': 2592000})

    def __init__(self, redis: Redis, config: LimiterConfig) -> None:
        self.redis = redis
        self.config = config
        self._script = self.redis.register_script(self._get_lua_script())

    def _get_lua_script(self) -> str:
        """Lua скрипт для атомарной проверки всех периодов.

        Returns:
            1 если все лимиты не превышены
            0 если хотя бы один лимит превышен

        """
        return """
        -- KEYS[1..N] - ключи для разных периодов
        -- ARGV[1..N] - лимиты для соответствующих периодов
        -- ARGV[N+1..2N] - TTL для соответствующих периодов

        local keys = KEYS
        local limits = {}
        local ttls = {}

        -- Заполняем лимиты и TTL
        local num_periods = #keys
        for i = 1, num_periods do
            limits[i] = tonumber(ARGV[i])
            ttls[i] = tonumber(ARGV[num_periods + i])
        end

        -- Проверяем все лимиты
        for i = 1, num_periods do
            local current = redis.call('GET', keys[i])
            if current and tonumber(current) >= limits[i] then
                return 0  -- Хотя бы один лимит превышен
            end
        end

        -- Все лимиты в норме, увеличиваем счетчики
        for i = 1, num_periods do
            local new = redis.call('INCR', keys[i])
            if new == 1 then
                redis.call('EXPIRE', keys[i], ttls[i])
            end
        end

        return 1  -- Успех
        """

    async def increment(self) -> bool:
        """Атомарно увеличить счетчики для всех периодов.

        Returns:
            True если успешно, False если лимит превышен.

        """
        if not self.config.limits:
            return True

        periods = list(self.PERIODS.keys())
        keys = [f'counter:{self.config.key}:{period}' for period in periods]

        limit_values = [self.config.limits[period] for period in periods]
        ttl_values = [self.PERIODS[period] for period in periods]
        args = limit_values + ttl_values

        result = await self._script(keys=keys, args=limit_values + ttl_values)

        return result == 1
