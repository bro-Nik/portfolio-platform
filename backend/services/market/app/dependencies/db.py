from shared.dependencies import db

from app.core import AsyncSessionLocal

deps = db.create_dependencies(AsyncSessionLocal)
get_session = deps.get_session
DBSession = deps.DBSession
