import asyncio
import logging

from redis.asyncio import Redis

logger = logging.getLogger(__name__)

LOCK_TTL = 3600
HEARTBEAT_INTERVAL = LOCK_TTL // 3


class TaskAlreadyRunningError(Exception):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f'Задача {task_id} уже выполняется')


class RedisTaskLock:
    def __init__(self, redis: Redis, key: str, ttl: int = LOCK_TTL) -> None:
        self.redis = redis
        self.key = key
        self.ttl = ttl
        self._renew_task: asyncio.Task | None = None

    async def __aenter__(self) -> 'RedisTaskLock':
        acquired = await self.redis.set(self.key, '1', nx=True, ex=self.ttl)
        if not acquired:
            raise TaskAlreadyRunningError(self.task_id_from_key())
        self._renew_task = asyncio.create_task(self._heartbeat())
        return self

    async def __aexit__(self, *args) -> None:
        if self._renew_task:
            self._renew_task.cancel()
            try:
                await self._renew_task
            except asyncio.CancelledError:
                pass
        await self.redis.delete(self.key)

    async def _heartbeat(self) -> None:
        try:
            while True:
                await asyncio.sleep(HEARTBEAT_INTERVAL)
                await self.redis.expire(self.key, self.ttl)
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception('Heartbeat failed for lock: %s', self.key)

    def task_id_from_key(self) -> int:
        return int(self.key.split(':')[-1])
