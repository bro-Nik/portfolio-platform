"""add is_archived columns, fix transaction FK to NO ACTION

Revision ID: a2b3c4d5e6f7
Revises: 5f8e3d2c1b4a
Create Date: 2026-07-18 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, None] = '5f8e3d2c1b4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # add is_archived columns
    op.add_column('portfolio', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('portfolio_asset', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('wallet', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('wallet_asset', sa.Column('is_archived', sa.Boolean(), nullable=False, server_default=sa.text('false')))

    # change transaction FK from CASCADE to NO ACTION (keep user_id FK as CASCADE)
    op.drop_constraint('fk_transaction_wallet_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_transaction_wallet2_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_transaction_portfolio_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_transaction_portfolio2_id', 'transaction', type_='foreignkey')

    op.create_foreign_key('fk_transaction_wallet_id', 'transaction', 'wallet', ['wallet_id'], ['id'])
    op.create_foreign_key('fk_transaction_wallet2_id', 'transaction', 'wallet', ['wallet2_id'], ['id'])
    op.create_foreign_key('fk_transaction_portfolio_id', 'transaction', 'portfolio', ['portfolio_id'], ['id'])
    op.create_foreign_key('fk_transaction_portfolio2_id', 'transaction', 'portfolio', ['portfolio2_id'], ['id'])


def downgrade() -> None:
    # restore CASCADE on transaction FKs
    op.drop_constraint('fk_transaction_portfolio2_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_transaction_portfolio_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_transaction_wallet2_id', 'transaction', type_='foreignkey')
    op.drop_constraint('fk_transaction_wallet_id', 'transaction', type_='foreignkey')

    op.create_foreign_key('fk_transaction_wallet_id', 'transaction', 'wallet', ['wallet_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_transaction_wallet2_id', 'transaction', 'wallet', ['wallet2_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_transaction_portfolio_id', 'transaction', 'portfolio', ['portfolio_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_transaction_portfolio2_id', 'transaction', 'portfolio', ['portfolio2_id'], ['id'], ondelete='CASCADE')

    # drop is_archived columns
    op.drop_column('wallet_asset', 'is_archived')
    op.drop_column('wallet', 'is_archived')
    op.drop_column('portfolio_asset', 'is_archived')
    op.drop_column('portfolio', 'is_archived')
