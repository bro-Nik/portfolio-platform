from dataclasses import dataclass

from app.common.exceptions.http import UnauthorizedException
from app.common.schemas import AuthUser


@dataclass
class Context:
    _actor: AuthUser | None
    client_ip: str
    request_id: str
    user_agent: str | None = None

    @property
    def actor(self) -> AuthUser:
        if self._actor is None:
            raise UnauthorizedException('Необходимо авторизоваться')
        return self._actor

    @property
    def actor_optional(self) -> AuthUser | None:
        return self._actor
