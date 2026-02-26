"""Rate limiting для защиты API от злоупотреблений.

Использует IP адрес для идентификации клиента.
Требует request: Request в роутах
"""

from fastapi import FastAPI, Request
from limits.storage import RedisStorage
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address


def get_ip(request: Request) -> str:
    """Получить IP клиента с учетом прокси."""
    # Заголовки в порядке приоритета
    ip_headers = ['X-Real-IP', 'CF-Connecting-IP', 'True-Client-IP', 'X-Forwarded-For']

    for header in ip_headers:
        ip = request.headers.get(header)
        if ip:
            # X-Forwarded-For может содержать цепочку: "client, proxy1, proxy2"
            # Берем первый IP (оригинальный клиент)
            return ip.split(',')[0].strip()

    return get_remote_address(request) or 'unknown'


def setup_rate_limiter(app: FastAPI, redis_url: str | None = None) -> None:
    """Настроить rate limiting."""
    if redis_url:
        limiter.storage = RedisStorage(redis_url)
    # memory storage по умолчанию
    
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)


limiter = Limiter(key_func=get_ip)


