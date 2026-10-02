from typing import Annotated

from dishka import FromDishka

from .deps import SessionDep, UserEmailReaderDep
from .di import WatchlistProvider
from app.common.dependencies import require_user
from app.modules.watchlist.services.alert import AlertService
from app.modules.watchlist.services.watchlist import WatchlistService

WatchlistServiceDep = Annotated[FromDishka[WatchlistService], ...]
AlertServiceDep = Annotated[FromDishka[AlertService], ...]

__all__ = [
    'AlertServiceDep',
    'SessionDep',
    'UserEmailReaderDep',
    'WatchlistProvider',
    'WatchlistServiceDep',
    'require_user',
]
