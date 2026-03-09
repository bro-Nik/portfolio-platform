from typing import Annotated
import uuid

from fastapi import Depends, Request
from shared.schemas import Context

from app.dependencies import CurrentUserOrNone


async def get_context(request: Request, current_user: CurrentUserOrNone) -> Context:
    """Зависимость для получения контекста."""
    return Context(
        _actor=current_user,
        client_ip=request.client.host,
        request_id=request.headers.get('X-Request-ID', str(uuid.uuid4())),
        user_agent=request.headers.get('user-agent'),
    )


Ctx = Annotated[Context, Depends(get_context)]
