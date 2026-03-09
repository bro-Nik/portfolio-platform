import uuid
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request

from shared.dependencies import auth
from shared.schemas import Context
from shared.utils import get_client_ip

auth_deps = auth.create_dependencies()


@dataclass
class ContextDependencies:
    """Контейнер со всеми зависимостями аутентификации."""

    Ctx: Annotated[Context, ...]


async def get_context(request: Request, current_user: auth_deps.CurrentUserOrNone) -> Context:
    """Зависимость для получения контекста."""
    return Context(
        _actor=current_user,
        client_ip=get_client_ip(request),
        request_id=request.headers.get('X-Request-ID', str(uuid.uuid4())),
        user_agent=request.headers.get('user-agent'),
    )


def create_dependencies() -> ContextDependencies:
    """Фабрика создает все зависимости для работы с контекстом."""
    Ctx = Annotated[Context, Depends(get_context)]

    return ContextDependencies(
        Ctx=Ctx,
    )
