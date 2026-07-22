"""add ticker_identifier table, supported_markets, price_updated_by

Revision ID: 0435a8e9f2b4
Revises: f6a7b8c9d0e1
Create Date: 2026-07-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0435a8e9f2b4'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ticker_identifier table
    op.create_table('ticker_identifier',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ticker_id', sa.Integer(), nullable=False),
        sa.Column('system', sa.String(64), nullable=False),
        sa.Column('value', sa.String(512), nullable=False),
        sa.ForeignKeyConstraint(['ticker_id'], ['ticker.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('system', 'value', name='uq_ticker_identifier_system_value'),
    )
    op.create_index(op.f('ix_ticker_identifier_ticker_id'), 'ticker_identifier', ['ticker_id'])

    # price_updated_by on ticker
    op.add_column('ticker', sa.Column('price_updated_by', sa.String(100), nullable=True))

    # supported_markets on provider
    op.add_column('provider', sa.Column('supported_markets', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('provider', 'supported_markets')
    op.drop_column('ticker', 'price_updated_by')
    op.drop_index(op.f('ix_ticker_identifier_ticker_id'), table_name='ticker_identifier')
    op.drop_table('ticker_identifier')
