from pathlib import Path
import sys

from alembic import context
from sqlalchemy import create_engine

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core import settings
from app.core.database import Base

# Import all models so they register on Base.metadata
import app.modules.auth.models  # noqa: F401
import app.modules.portfolios.models  # noqa: F401
import app.modules.market.models  # noqa: F401

config = context.config
target_metadata = Base.metadata


def run_migrations():
    engine = create_engine(
        settings.sync_db_url,
        pool_pre_ping=True,
        echo=False,
    )
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError('Offline mode not configured')

run_migrations()
