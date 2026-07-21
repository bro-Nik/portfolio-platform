"""add ticker_external_id table

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-07-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PROVIDER_BY_PREFIX = {
    'cr-': 'CoinGecko',
    'st-': 'Polygon',
    'cu-': 'CurrencyLayer',
}


def upgrade() -> None:
    op.create_table(
        'ticker_external_id',
        sa.Column('ticker_id', sa.String(256), sa.ForeignKey('ticker.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('provider_name', sa.String(100), primary_key=True),
        sa.Column('external_id', sa.String(256), nullable=False, index=True),
        sa.PrimaryKeyConstraint('ticker_id', 'provider_name'),
    )

    conn = op.get_bind()

    ticker_table = sa.table(
        'ticker',
        sa.Column('id', sa.String(256)),
    )

    result = conn.execute(
        sa.select(ticker_table.c.id)
    ).fetchall()

    ticker_external_id_table = sa.table(
        'ticker_external_id',
        sa.Column('ticker_id', sa.String(256)),
        sa.Column('provider_name', sa.String(100)),
        sa.Column('external_id', sa.String(256)),
    )

    for (ticker_id,) in result:
        provider_name = None
        for prefix, provider in PROVIDER_BY_PREFIX.items():
            if ticker_id.startswith(prefix):
                provider_name = provider
                break

        if not provider_name:
            continue

        external_id = ticker_id.removeprefix(prefix)
        conn.execute(
            sa.insert(ticker_external_id_table).values(
                ticker_id=ticker_id,
                provider_name=provider_name,
                external_id=external_id,
            )
        )


def downgrade() -> None:
    op.drop_table('ticker_external_id')
