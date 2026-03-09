"""add user_id columns

Revision ID: a9bb57674647
Revises: 1125c5da0c57
Create Date: 2026-03-06 12:05:13.746027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9bb57674647'
down_revision: Union[str, Sequence[str], None] = '1125c5da0c57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем user_id
    op.add_column('portfolio_asset', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('transaction', sa.Column('user_id', sa.Integer(), nullable=True))
    op.add_column('wallet_asset', sa.Column('user_id', sa.Integer(), nullable=True))
    
    # Заполняем существующие записи
    op.execute("""
        UPDATE portfolio_asset 
        SET user_id = (
            SELECT user_id FROM portfolio 
            WHERE portfolio.id = portfolio_asset.portfolio_id
        )
    """)
    
    op.execute("""
        UPDATE wallet_asset 
        SET user_id = (
            SELECT user_id FROM wallet 
            WHERE wallet.id = wallet_asset.wallet_id
        )
    """)
    
    op.execute("""
        UPDATE transaction 
        SET user_id = COALESCE(
            (SELECT user_id FROM portfolio WHERE portfolio.id = transaction.portfolio_id),
            (SELECT user_id FROM wallet WHERE wallet.id = transaction.wallet_id),
            0
        )
    """)
    
    # Делаем колонки NOT NULL
    op.alter_column('portfolio_asset', 'user_id', nullable=False)
    op.alter_column('transaction', 'user_id', nullable=False)
    op.alter_column('wallet_asset', 'user_id', nullable=False)


def downgrade() -> None:
    # Удаляем колонки
    op.drop_column('portfolio_asset', 'user_id')
    op.drop_column('transaction', 'user_id')
    op.drop_column('wallet_asset', 'user_id')
