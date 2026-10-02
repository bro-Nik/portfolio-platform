"""Листовые Dishka-алиасы: без импорта сервисов, чтобы tasks-модуль не давал циклов."""

from typing import Annotated

from dishka import FromDishka
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.watchlist.protocols import UserEmailReader

SessionDep = Annotated[FromDishka[AsyncSession], ...]
UserEmailReaderDep = Annotated[FromDishka[UserEmailReader], ...]
