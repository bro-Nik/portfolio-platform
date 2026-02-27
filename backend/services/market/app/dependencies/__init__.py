from typing import Annotated

from shared.dependencies import db
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal

get_db = db.create_session_dependency(AsyncSessionLocal)
DBSession = Annotated[AsyncSession, get_db]
