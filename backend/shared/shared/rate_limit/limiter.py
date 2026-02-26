"""Rate limiting для защиты API от злоупотреблений.

Использует IP адрес для идентификации клиента.
Требует request: Request в роутах
"""

from fastapi import FastAPI
from limits.storage import RedisStorage
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from shared.utils import get_client_ip


def setup_rate_limiter(app: FastAPI, redis_url: str | None = None) -> None:
    """Настроить rate limiting."""
    if redis_url:
        limiter.storage = RedisStorage(redis_url)
    # memory storage по умолчанию
    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)


limiter = Limiter(key_func=get_client_ip)
