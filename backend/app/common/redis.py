import redis.asyncio as redis
from redis.asyncio import Redis

from app.core import settings

_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = redis.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            socket_timeout=settings.redis_timeout,
        )
    return _redis
