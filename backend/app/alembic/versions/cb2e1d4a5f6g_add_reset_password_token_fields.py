"""add reset_password_token fields to users table

Revision ID: cb2e1d4a5f6g
Revises: 0e9efe973beb
Create Date: 2026-07-17 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb2e1d4a5f6g'
down_revision: Union[str, None] = 'f3b1e2d4a5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('reset_password_token_hash', sa.String(64), nullable=True))
    op.add_column('users', sa.Column('reset_password_token_expires_at', sa.BigInteger(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'reset_password_token_expires_at')
    op.drop_column('users', 'reset_password_token_hash')
