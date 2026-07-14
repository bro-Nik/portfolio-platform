from fastapi import FastAPI
from limits.storage import RedisStorage
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.common.utils import get_client_ip


def setup_rate_limiter(app: FastAPI, redis_url: str | None = None) -> None:
    if redis_url:
        limiter.storage = RedisStorage(redis_url)

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


limiter = Limiter(key_func=get_client_ip)
