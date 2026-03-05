from pathlib import Path
import sys

from alembic import context
from sqlalchemy import create_engine

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from app.core import settings
from app.models import Base

config = context.config
target_metadata = Base.metadata


def run_migrations() -> None:
    """Запуск миграций."""
    engine = create_engine(
        settings.sync_db_url,
        pool_pre_ping=True,
        echo=False,
    )
    with engine.connect() as connection:
        do_run_migrations(connection)


def do_run_migrations(connection) -> None:
    """Выполнение миграций через синхронное соединение."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError('Offline mode не настроен')

run_migrations()
