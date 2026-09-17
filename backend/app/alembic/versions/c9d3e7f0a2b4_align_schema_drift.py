"""align schema drift flagged by alembic check

`alembic check` on a database built purely from migrations reported four
differences that `create_all` in tests never surfaced:

- ticker_id stayed nullable on portfolio_asset / transaction / wallet_asset,
  because f6a7b8c9d0e1 renamed the *_new columns back without restoring
  NOT NULL, while the models declare it required;
- the index on refresh_tokens.token declared by the model was never recreated
  after the column became nullable.

The leftover uq_ticker_id_new on ticker.id is kept and declared on the model
instead: foreign keys rely on it, so dropping it would cascade them away.

Revision ID: c9d3e7f0a2b4
Revises: b8c2d4e6f1a3
Create Date: 2026-10-02 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = 'c9d3e7f0a2b4'
down_revision: str | None = 'b8c2d4e6f1a3'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


TICKER_ID_TABLES = ('portfolio_asset', 'transaction', 'wallet_asset')


def upgrade() -> None:
    for table in TICKER_ID_TABLES:
        op.alter_column(table, 'ticker_id', nullable=False)
    op.create_index('ix_refresh_tokens_token', 'refresh_tokens', ['token'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_refresh_tokens_token', table_name='refresh_tokens')
    for table in TICKER_ID_TABLES:
        op.alter_column(table, 'ticker_id', nullable=True)
