from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from app.core.database import SyncSessionLocal


@contextmanager
def get_sync_db() -> Generator[Session, None, None]:
    """Синхронный контекстный менеджер для сессии БД."""
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
