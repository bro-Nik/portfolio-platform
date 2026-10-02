"""add watchlist_item and price_alert tables

Revision ID: f0a1b2c3d4e5
Revises: c9d3e7f0a2b4
Create Date: 2026-10-09 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f0a1b2c3d4e5'
down_revision: str | None = 'c9d3e7f0a2b4'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'watchlist_item',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ticker_id', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'ticker_id', name='uq_watchlist_item_user_ticker'),
    )
    op.create_index('ix_watchlist_item_id', 'watchlist_item', ['id'], unique=False)
    op.create_index('ix_watchlist_item_user_id', 'watchlist_item', ['user_id'], unique=False)
    op.create_index('ix_watchlist_item_ticker_id', 'watchlist_item', ['ticker_id'], unique=False)

    op.create_table(
        'price_alert',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('watchlist_item_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('direction', sa.String(8), nullable=False),
        sa.Column('target_price_usd', sa.Numeric(), nullable=False),
        sa.Column('currency_symbol', sa.String(16), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('triggered_price', sa.Float(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['watchlist_item_id'], ['watchlist_item.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_price_alert_id', 'price_alert', ['id'], unique=False)
    op.create_index('ix_price_alert_watchlist_item_id', 'price_alert', ['watchlist_item_id'], unique=False)
    op.create_index('ix_price_alert_user_id', 'price_alert', ['user_id'], unique=False)
    op.create_index('ix_price_alert_is_active', 'price_alert', ['is_active'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_price_alert_is_active', table_name='price_alert')
    op.drop_index('ix_price_alert_user_id', table_name='price_alert')
    op.drop_index('ix_price_alert_watchlist_item_id', table_name='price_alert')
    op.drop_index('ix_price_alert_id', table_name='price_alert')
    op.drop_table('price_alert')
    op.drop_index('ix_watchlist_item_ticker_id', table_name='watchlist_item')
    op.drop_index('ix_watchlist_item_user_id', table_name='watchlist_item')
    op.drop_index('ix_watchlist_item_id', table_name='watchlist_item')
    op.drop_table('watchlist_item')
