"""add realized_profit and total_invested to portfolio_asset

Revision ID: 558fbe00123e
Revises: a9bb57674647
Create Date: 2026-06-05 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '558fbe00123e'
down_revision: Union[str, Sequence[str], None] = 'a9bb57674647'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('portfolio_asset', sa.Column('realized_profit', sa.Numeric(), nullable=False, server_default=sa.text('0')))
    op.add_column('portfolio_asset', sa.Column('total_invested', sa.Numeric(), nullable=False, server_default=sa.text('0')))


def downgrade() -> None:
    op.drop_column('portfolio_asset', 'total_invested')
    op.drop_column('portfolio_asset', 'realized_profit')
