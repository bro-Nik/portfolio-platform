from dataclasses import dataclass

from shared.exceptions.http import UnauthorizedException
from shared.schemas import AuthUser


@dataclass
class Context:
    """Контекст запроса."""

    _actor: AuthUser | None
    client_ip: str
    request_id: str
    user_agent: str | None = None

    @property
    def actor(self) -> AuthUser:
        """Получение пользователя с проверкой наличия."""
        if self._actor is None:
            # TODO: Переделать на AuthenticationError
            raise UnauthorizedException('Необходимо авторизоваться')
        return self._actor

    @property
    def actor_optional(self) -> AuthUser | None:
        """Получение опционального пользователя."""
        return self._actor
