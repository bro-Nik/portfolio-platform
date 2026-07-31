"""add scope column to tag

Revision ID: 7a1b2c3d4e5f
Revises: 5a6b7c8d9e0f
Create Date: 2026-07-31 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '7a1b2c3d4e5f'
down_revision: Union[str, None] = '5a6b7c8d9e0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tag', sa.Column('scope', sa.String(32), nullable=False))


def downgrade() -> None:
    op.drop_column('tag', 'scope')
