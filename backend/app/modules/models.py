"""Единая точка регистрации всех ORM-моделей.

SQLAlchemy разрешает строковые связи (`Mapped['User']`) только когда оба класса
уже зарегистрированы в реестре, поэтому `configure_mappers()` падал, если был
импортирован лишь один модуль моделей. Импортируйте этот модуль вместо
отдельных `app.modules.*.models` — он же используется alembic, seed и тестами.
"""

from app.modules import auth, market, portfolios, tags, watchlist
from app.modules.auth import models as auth_models
from app.modules.market import models as market_models
from app.modules.portfolios import models as portfolios_models
from app.modules.tags import models as tags_models
from app.modules.watchlist import models as watchlist_models

__all__ = [
    'auth',
    'auth_models',
    'market',
    'market_models',
    'portfolios',
    'portfolios_models',
    'tags',
    'tags_models',
    'watchlist',
    'watchlist_models',
]
