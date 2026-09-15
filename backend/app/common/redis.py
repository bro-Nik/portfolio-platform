import redis.asyncio as redis
from redis.asyncio import Redis

from app.core import settings


def create_redis() -> Redis:
    """Клиент Redis для DI-контейнера: закрывается вместе с приложением."""
    return redis.from_url(
        settings.redis_url,
        max_connections=settings.redis_max_connections,
        socket_timeout=settings.redis_timeout,
    )


# Глобальный клиент для мест вне контейнера (скрипты, ленивый доступ).
# Контейнер использует create_redis, чтобы владение клиентом было явным.
_shared_redis: Redis | None = None


def get_redis() -> Redis:
    global _shared_redis  # noqa: PLW0603
    if _shared_redis is None:
        _shared_redis = create_redis()
    return _shared_redis


async def close_redis() -> None:
    global _shared_redis  # noqa: PLW0603
    if _shared_redis is not None:
        await _shared_redis.aclose()
        _shared_redis = None
