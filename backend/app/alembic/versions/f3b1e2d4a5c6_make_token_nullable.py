"""make token column nullable

Revision ID: f3b1e2d4a5c6
Revises: 0e9efe973beb
Create Date: 2026-07-17 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f3b1e2d4a5c6'
down_revision: Union[str, None] = '0e9efe973beb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index('ix_refresh_tokens_token', table_name='refresh_tokens')
    op.alter_column('refresh_tokens', 'token', nullable=True)


def downgrade() -> None:
    op.alter_column('refresh_tokens', 'token', nullable=False)
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=True)
