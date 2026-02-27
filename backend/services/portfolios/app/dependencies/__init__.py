from typing import Annotated

from fastapi import Depends
from shared.dependencies import auth

from app.core.config import settings
from app.schemas import AuthUser

from .database import get_db_session
from .redis import redis_client
from .services import (
    get_portfolio_asset_service,
    get_portfolio_service,
    get_transaction_service,
    get_wallet_asset_service,
    get_wallet_service,
)

get_current_user = auth.create_auth_dependency(
    jwt_secret=settings.jwt_secret,
    jwt_algorithm=settings.jwt_algorithm,
)

CurrentUser = Annotated[AuthUser, get_current_user]
