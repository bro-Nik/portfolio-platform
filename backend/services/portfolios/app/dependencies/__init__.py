from typing import Annotated

from fastapi import Depends
from shared.dependencies import auth, db
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import AsyncSessionLocal, settings
from app.schemas import AuthUser

from .redis import redis_client

get_current_user = auth.create_auth_dependency(
    jwt_secret=settings.jwt_secret,
    jwt_algorithm=settings.jwt_algorithm,
)

CurrentUser = Annotated[AuthUser, get_current_user]

get_db = db.create_session_dependency(AsyncSessionLocal)
DBSession = Annotated[AsyncSession, get_db]

from .services import (
    get_portfolio_asset_service,
    get_portfolio_service,
    get_transaction_service,
    get_wallet_asset_service,
    get_wallet_service,
)
