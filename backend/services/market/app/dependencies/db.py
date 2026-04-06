from app.core import SessionLocal
from shared.dependencies import db

deps = db.create_dependencies(SessionLocal)
get_session = deps.get_session
DBSession = deps.DBSession
