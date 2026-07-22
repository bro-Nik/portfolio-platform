"""add missing indexes

Revision ID: 5a6b7c8d9e0f
Revises: 0435a8e9f2b4
Create Date: 2026-07-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = '5a6b7c8d9e0f'
down_revision: Union[str, None] = '0435a8e9f2b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === auth ===
    op.create_index(op.f('ix_refresh_tokens_user_id'), 'refresh_tokens', ['user_id'])
    op.create_index(op.f('ix_login_sessions_user_id'), 'login_sessions', ['user_id'])

    # === portfolios: portfolio_asset ===
    op.create_index(op.f('ix_portfolio_asset_portfolio_id'), 'portfolio_asset', ['portfolio_id'])
    op.create_index(op.f('ix_portfolio_asset_ticker_id'), 'portfolio_asset', ['ticker_id'])
    op.create_index(op.f('ix_portfolio_asset_user_id'), 'portfolio_asset', ['user_id'])
    op.create_index('ix_portfolio_asset_portfolio_ticker', 'portfolio_asset', ['portfolio_id', 'ticker_id'])

    # === portfolios: wallet_asset ===
    op.create_index(op.f('ix_wallet_asset_wallet_id'), 'wallet_asset', ['wallet_id'])
    op.create_index(op.f('ix_wallet_asset_ticker_id'), 'wallet_asset', ['ticker_id'])
    op.create_index(op.f('ix_wallet_asset_user_id'), 'wallet_asset', ['user_id'])
    op.create_index('ix_wallet_asset_wallet_ticker', 'wallet_asset', ['wallet_id', 'ticker_id'])

    # === portfolios: transaction ===
    op.create_index(op.f('ix_transaction_date'), 'transaction', ['date'])
    op.create_index(op.f('ix_transaction_ticker_id'), 'transaction', ['ticker_id'])
    op.create_index(op.f('ix_transaction_ticker2_id'), 'transaction', ['ticker2_id'])
    op.create_index(op.f('ix_transaction_wallet_id'), 'transaction', ['wallet_id'])
    op.create_index(op.f('ix_transaction_wallet2_id'), 'transaction', ['wallet2_id'])
    op.create_index(op.f('ix_transaction_portfolio_id'), 'transaction', ['portfolio_id'])
    op.create_index(op.f('ix_transaction_portfolio2_id'), 'transaction', ['portfolio2_id'])
    op.create_index(op.f('ix_transaction_user_id'), 'transaction', ['user_id'])

    # === portfolios: taggable ===
    op.create_index(op.f('ix_taggable_tag_id'), 'taggable', ['tag_id'])
    op.create_index('ix_taggable_entity_type_entity_id', 'taggable', ['entity_type', 'entity_id'])

    # === market: provider ===
    op.create_index(op.f('ix_provider_is_active'), 'provider', ['is_active'])

    # === market: task ===
    op.create_index(op.f('ix_task_name'), 'task', ['name'])
    op.create_index(op.f('ix_task_is_active'), 'task', ['is_active'])


def downgrade() -> None:
    # === auth ===
    op.drop_index(op.f('ix_refresh_tokens_user_id'), table_name='refresh_tokens')
    op.drop_index(op.f('ix_login_sessions_user_id'), table_name='login_sessions')

    # === portfolios: portfolio_asset ===
    op.drop_index(op.f('ix_portfolio_asset_portfolio_id'), table_name='portfolio_asset')
    op.drop_index(op.f('ix_portfolio_asset_ticker_id'), table_name='portfolio_asset')
    op.drop_index(op.f('ix_portfolio_asset_user_id'), table_name='portfolio_asset')
    op.drop_index('ix_portfolio_asset_portfolio_ticker', table_name='portfolio_asset')

    # === portfolios: wallet_asset ===
    op.drop_index(op.f('ix_wallet_asset_wallet_id'), table_name='wallet_asset')
    op.drop_index(op.f('ix_wallet_asset_ticker_id'), table_name='wallet_asset')
    op.drop_index(op.f('ix_wallet_asset_user_id'), table_name='wallet_asset')
    op.drop_index('ix_wallet_asset_wallet_ticker', table_name='wallet_asset')

    # === portfolios: transaction ===
    op.drop_index(op.f('ix_transaction_date'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_ticker_id'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_ticker2_id'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_wallet_id'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_wallet2_id'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_portfolio_id'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_portfolio2_id'), table_name='transaction')
    op.drop_index(op.f('ix_transaction_user_id'), table_name='transaction')

    # === portfolios: taggable ===
    op.drop_index(op.f('ix_taggable_tag_id'), table_name='taggable')
    op.drop_index('ix_taggable_entity_type_entity_id', table_name='taggable')

    # === market: provider ===
    op.drop_index(op.f('ix_provider_is_active'), table_name='provider')

    # === market: task ===
    op.drop_index(op.f('ix_task_name'), table_name='task')
    op.drop_index(op.f('ix_task_is_active'), table_name='task')
