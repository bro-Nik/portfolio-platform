"""switch ticker.id to autoincrement int

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-07-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _get_old_to_new_mapping() -> dict[str, int]:
    conn = op.get_bind()
    ticker_table = sa.table(
        'ticker',
        sa.Column('id', sa.String(256)),
        sa.Column('id_new', sa.Integer()),
    )
    rows = conn.execute(
        sa.select(ticker_table.c.id, ticker_table.c.id_new)
    ).fetchall()
    return {row.id: row.id_new for row in rows}


def upgrade() -> None:
    conn = op.get_bind()

    # === ticker ===
    op.add_column('ticker', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))

    op.add_column('ticker', sa.Column('id_new', sa.Integer(), nullable=True))
    op.execute("CREATE SEQUENCE IF NOT EXISTS ticker_id_new_seq")
    op.execute("SELECT setval('ticker_id_new_seq', COALESCE((SELECT COUNT(*) FROM ticker), 0), true)")
    op.execute("UPDATE ticker SET id_new = nextval('ticker_id_new_seq') WHERE id_new IS NULL")
    op.alter_column('ticker', 'id_new', nullable=False)
    op.execute("ALTER TABLE ticker ALTER COLUMN id_new SET DEFAULT nextval('ticker_id_new_seq')")
    op.execute("ALTER SEQUENCE ticker_id_new_seq OWNED BY ticker.id_new")
    op.create_unique_constraint('uq_ticker_id_new', 'ticker', ['id_new'])

    old_to_new = _get_old_to_new_mapping()

    # === ticker_external_id ===
    op.execute("ALTER TABLE ticker_external_id DROP CONSTRAINT IF EXISTS ticker_external_id_ticker_id_fkey")
    op.drop_constraint('ticker_external_id_pkey', 'ticker_external_id', type_='primary')

    op.add_column('ticker_external_id', sa.Column('ticker_id_new', sa.Integer(), nullable=True))
    ext_id_table = sa.table(
        'ticker_external_id',
        sa.Column('ticker_id', sa.String(256)),
        sa.Column('ticker_id_new', sa.Integer()),
        sa.Column('provider_name', sa.String(100)),
    )
    for old_id, new_id in old_to_new.items():
        conn.execute(
            sa.update(ext_id_table)
            .where(ext_id_table.c.ticker_id == old_id)
            .values(ticker_id_new=new_id)
        )
    op.execute("DELETE FROM ticker_external_id WHERE ticker_id_new IS NULL")
    op.drop_column('ticker_external_id', 'ticker_id')
    op.alter_column('ticker_external_id', 'ticker_id_new', new_column_name='ticker_id', nullable=False)
    op.create_primary_key('pk_ticker_external_id', 'ticker_external_id', ['ticker_id', 'provider_name'])
    op.create_foreign_key('fk_ticker_external_id_ticker', 'ticker_external_id', 'ticker', ['ticker_id'], ['id_new'], ondelete='CASCADE')

    # === portfolio_asset ===
    op.add_column('portfolio_asset', sa.Column('ticker_id_new', sa.Integer(), nullable=True))
    pa_table = sa.table(
        'portfolio_asset',
        sa.Column('ticker_id', sa.String(256)),
        sa.Column('ticker_id_new', sa.Integer()),
    )
    for old_id, new_id in old_to_new.items():
        conn.execute(
            sa.update(pa_table)
            .where(pa_table.c.ticker_id == old_id)
            .values(ticker_id_new=new_id)
        )
    op.drop_column('portfolio_asset', 'ticker_id')
    op.alter_column('portfolio_asset', 'ticker_id_new', new_column_name='ticker_id')

    # === wallet_asset ===
    op.add_column('wallet_asset', sa.Column('ticker_id_new', sa.Integer(), nullable=True))
    wa_table = sa.table(
        'wallet_asset',
        sa.Column('ticker_id', sa.String(256)),
        sa.Column('ticker_id_new', sa.Integer()),
    )
    for old_id, new_id in old_to_new.items():
        conn.execute(
            sa.update(wa_table)
            .where(wa_table.c.ticker_id == old_id)
            .values(ticker_id_new=new_id)
        )
    op.drop_column('wallet_asset', 'ticker_id')
    op.alter_column('wallet_asset', 'ticker_id_new', new_column_name='ticker_id')

    # === transaction ===
    op.add_column('transaction', sa.Column('ticker_id_new', sa.Integer(), nullable=True))
    op.add_column('transaction', sa.Column('ticker2_id_new', sa.Integer(), nullable=True))
    txn_table = sa.table(
        'transaction',
        sa.Column('ticker_id', sa.String(32)),
        sa.Column('ticker2_id', sa.String(32)),
        sa.Column('ticker_id_new', sa.Integer()),
        sa.Column('ticker2_id_new', sa.Integer()),
    )
    for old_id, new_id in old_to_new.items():
        conn.execute(
            sa.update(txn_table)
            .where(txn_table.c.ticker_id == old_id)
            .values(ticker_id_new=new_id)
        )
        conn.execute(
            sa.update(txn_table)
            .where(txn_table.c.ticker2_id == old_id)
            .values(ticker2_id_new=new_id)
        )
    op.drop_column('transaction', 'ticker_id')
    op.drop_column('transaction', 'ticker2_id')
    op.alter_column('transaction', 'ticker_id_new', new_column_name='ticker_id')
    op.alter_column('transaction', 'ticker2_id_new', new_column_name='ticker2_id')

    # === finalize ticker PK swap ===
    op.drop_constraint('ticker_pkey', 'ticker', type_='primary')
    op.drop_column('ticker', 'id')
    op.alter_column('ticker', 'id_new', new_column_name='id')
    op.create_primary_key('pk_ticker', 'ticker', ['id'])


def downgrade() -> None:
    conn = op.get_bind()

    # Restore old string IDs on ticker
    new_to_old = {}
    op.execute("""
        UPDATE ticker SET id_new = id
    """)
    op.add_column('ticker', sa.Column('id_old', sa.String(256)))
    ticker_table = sa.table('ticker', sa.Column('id', sa.Integer()), sa.Column('id_old', sa.String(256)))

    conn.execute(
        sa.update(ticker_table)
        .values(id_old=sa.cast(ticker_table.c.id, sa.String))
    )

    # transaction
    op.add_column('transaction', sa.Column('ticker_id_old', sa.String(32), nullable=True))
    op.add_column('transaction', sa.Column('ticker2_id_old', sa.String(32), nullable=True))
    txn_table = sa.table(
        'transaction',
        sa.Column('ticker_id', sa.Integer()),
        sa.Column('ticker2_id', sa.Integer()),
        sa.Column('ticker_id_old', sa.String(32)),
        sa.Column('ticker2_id_old', sa.String(32)),
    )
    conn.execute(
        sa.update(txn_table)
        .values(ticker_id_old=sa.cast(txn_table.c.ticker_id, sa.String))
    )
    conn.execute(
        sa.update(txn_table)
        .where(txn_table.c.ticker2_id.isnot(None))
        .values(ticker2_id_old=sa.cast(txn_table.c.ticker2_id, sa.String))
    )
    op.drop_column('transaction', 'ticker_id')
    op.drop_column('transaction', 'ticker2_id')
    op.alter_column('transaction', 'ticker_id_old', new_column_name='ticker_id')
    op.alter_column('transaction', 'ticker2_id_old', new_column_name='ticker2_id')

    # wallet_asset
    op.add_column('wallet_asset', sa.Column('ticker_id_old', sa.String(256), nullable=True))
    wa_table = sa.table('wallet_asset', sa.Column('ticker_id', sa.Integer()), sa.Column('ticker_id_old', sa.String(256)))
    conn.execute(
        sa.update(wa_table)
        .values(ticker_id_old=sa.cast(wa_table.c.ticker_id, sa.String))
    )
    op.drop_column('wallet_asset', 'ticker_id')
    op.alter_column('wallet_asset', 'ticker_id_old', new_column_name='ticker_id')

    # portfolio_asset
    op.add_column('portfolio_asset', sa.Column('ticker_id_old', sa.String(256), nullable=True))
    pa_table = sa.table('portfolio_asset', sa.Column('ticker_id', sa.Integer()), sa.Column('ticker_id_old', sa.String(256)))
    conn.execute(
        sa.update(pa_table)
        .values(ticker_id_old=sa.cast(pa_table.c.ticker_id, sa.String))
    )
    op.drop_column('portfolio_asset', 'ticker_id')
    op.alter_column('portfolio_asset', 'ticker_id_old', new_column_name='ticker_id')

    # ticker_external_id
    op.drop_constraint('fk_ticker_external_id_ticker', 'ticker_external_id', type_='foreignkey')
    op.drop_constraint('pk_ticker_external_id', 'ticker_external_id', type_='primary')

    op.add_column('ticker_external_id', sa.Column('ticker_id_old', sa.String(256), nullable=True))
    ext_id_table = sa.table(
        'ticker_external_id',
        sa.Column('ticker_id', sa.Integer()),
        sa.Column('ticker_id_old', sa.String(256)),
        sa.Column('provider_name', sa.String(100)),
    )
    conn.execute(
        sa.update(ext_id_table)
        .values(ticker_id_old=sa.cast(ext_id_table.c.ticker_id, sa.String))
    )
    op.drop_column('ticker_external_id', 'ticker_id')
    op.alter_column('ticker_external_id', 'ticker_id_old', new_column_name='ticker_id', nullable=False)
    op.create_primary_key('ticker_external_id_pkey', 'ticker_external_id', ['ticker_id', 'provider_name'])
    op.create_foreign_key(None, 'ticker_external_id', 'ticker', ['ticker_id'], ['id_old'], ondelete='CASCADE')

    # ticker PK swap back
    op.drop_constraint('pk_ticker', 'ticker', type_='primary')
    op.drop_column('ticker', 'id_old')
    op.alter_column('ticker', 'id', new_column_name='id_new')

    op.add_column('ticker', sa.Column('id', sa.String(256)))
    old_ticker = sa.table('ticker', sa.Column('id_new', sa.Integer()), sa.Column('id', sa.String(256)))

    new_ids = conn.execute(sa.select(old_ticker.c.id_new)).fetchall()
    for (nid,) in new_ids:
        conn.execute(
            sa.update(old_ticker)
            .where(old_ticker.c.id_new == nid)
            .values(id=sa.cast(nid, sa.String))
        )

    op.alter_column('ticker', 'id', nullable=False)
    op.create_primary_key('ticker_pkey', 'ticker', ['id'])
    op.drop_column('ticker', 'id_new')
    op.drop_column('ticker', 'is_active')
