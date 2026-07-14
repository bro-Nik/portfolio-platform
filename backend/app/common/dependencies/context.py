import uuid
from typing import Annotated

from fastapi import Depends, Request

from app.common.dependencies import auth
from app.common.schemas import Context
from app.common.utils import get_client_ip


async def get_context(request: Request, current_user: auth.CurrentUserOrNone) -> Context:
    return Context(
        _actor=current_user,
        client_ip=get_client_ip(request),
        request_id=request.headers.get('X-Request-ID', str(uuid.uuid4())),
        user_agent=request.headers.get('user-agent'),
    )


Ctx = Annotated[Context, Depends(get_context)]
