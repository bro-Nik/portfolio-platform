"""Rate limiting для защиты API от злоупотреблений.

Использует IP адрес для идентификации клиента.
Требует request: Request в роутах
"""

# TODO: Redis

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.utils import get_real_ip


def get_ip(request: Request) -> str:
    ip = get_real_ip(request)

    return ip if ip else get_remote_address(request)


limiter = Limiter(key_func=get_ip)
