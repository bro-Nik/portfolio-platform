"""add ondelete CASCADE to all user-facing FK constraints

Revision ID: 5f8e3d2c1b4a
Revises: 41e8f2b6c3d0
Create Date: 2026-07-18 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '5f8e3d2c1b4a'
down_revision: Union[str, None] = '41e8f2b6c3d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing FK that lack CASCADE
    op.drop_constraint('portfolio_asset_portfolio_id_fkey', 'portfolio_asset', type_='foreignkey')
    op.drop_constraint('wallet_asset_wallet_id_fkey', 'wallet_asset', type_='foreignkey')

    # Recreate with ON DELETE CASCADE
    op.create_foreign_key(
        'portfolio_asset_portfolio_id_fkey', 'portfolio_asset', 'portfolio',
        ['portfolio_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'wallet_asset_wallet_id_fkey', 'wallet_asset', 'wallet',
        ['wallet_id'], ['id'], ondelete='CASCADE',
    )

    # Add new FK constraints with CASCADE for user_id columns
    op.create_foreign_key(
        'fk_portfolio_user_id', 'portfolio', 'users',
        ['user_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_portfolio_asset_user_id', 'portfolio_asset', 'users',
        ['user_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_wallet_user_id', 'wallet', 'users',
        ['user_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_wallet_asset_user_id', 'wallet_asset', 'users',
        ['user_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_tag_user_id', 'tag', 'users',
        ['user_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_transaction_user_id', 'transaction', 'users',
        ['user_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_transaction_wallet_id', 'transaction', 'wallet',
        ['wallet_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_transaction_wallet2_id', 'transaction', 'wallet',
        ['wallet2_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_transaction_portfolio_id', 'transaction', 'portfolio',
        ['portfolio_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'fk_transaction_portfolio2_id', 'transaction', 'portfolio',
        ['portfolio2_id'], ['id'], ondelete='CASCADE',
    )


def downgrade() -> None:
    # Remove new FK constraints
    op.drop_constraint('fk_transaction_portfolio2_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_transaction_portfolio_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_transaction_wallet2_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_transaction_wallet_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_transaction_user_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_tag_user_id', 'tag', type_='foreignkey')
    op.drop_constraint('fk_wallet_asset_user_id', 'wallet_asset', type_='foreignkey')
    op.drop_constraint('fk_wallet_user_id', 'wallet', type_='foreignkey')
    op.drop_constraint('fk_portfolio_asset_user_id', 'portfolio_asset', type_='foreignkey')
    op.drop_constraint('fk_portfolio_user_id', 'portfolio', type_='foreignkey')

    # Restore original FK without CASCADE
    op.drop_constraint('wallet_asset_wallet_id_fkey', 'wallet_asset', type_='foreignkey')
    op.drop_constraint('portfolio_asset_portfolio_id_fkey', 'portfolio_asset', type_='foreignkey')

    op.create_foreign_key(
        'wallet_asset_wallet_id_fkey', 'wallet_asset', 'wallet',
        ['wallet_id'], ['id'],
    )
    op.create_foreign_key(
        'portfolio_asset_portfolio_id_fkey', 'portfolio_asset', 'portfolio',
        ['portfolio_id'], ['id'],
    )
