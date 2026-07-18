"""drop reset_password_token fields from users

Revision ID: 41e8f2b6c3d0
Revises: cb2e1d4a5f6g
Create Date: 2026-07-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41e8f2b6c3d0'
down_revision: Union[str, None] = 'cb2e1d4a5f6g'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('users', 'reset_password_token_hash')
    op.drop_column('users', 'reset_password_token_expires_at')


def downgrade() -> None:
    op.add_column('users', sa.Column('reset_password_token_hash', sa.String(64), nullable=True))
    op.add_column('users', sa.Column('reset_password_token_expires_at', sa.BigInteger(), nullable=True))
