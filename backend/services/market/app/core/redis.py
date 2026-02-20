import redis

from app.core.config import settings

_celery_client: redis.Redis | None = None


def get_celery_redis() -> redis.Redis:
    """Для Celery (broker и backend)."""
    global _celery_client

    if _celery_client is None:
        _celery_client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=False,
            socket_connect_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30,
        )
    return _celery_client
