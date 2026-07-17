"""add token_hash and is_verified

Revision ID: 0e9efe973beb
Revises: 01773f2e3fa1
Create Date: 2026-07-17 16:06:51.640823

"""
from hashlib import sha256
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e9efe973beb'
down_revision: Union[str, None] = '01773f2e3fa1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('refresh_tokens', sa.Column('token_hash', sa.String(64), nullable=True))
    op.create_index(op.f('ix_refresh_tokens_token_hash'), 'refresh_tokens', ['token_hash'], unique=True)

    conn = op.get_bind()
    tokens_table = sa.table(
        'refresh_tokens',
        sa.Column('id', sa.Integer),
        sa.Column('token', sa.String(512)),
        sa.Column('token_hash', sa.String(64)),
    )
    rows = conn.execute(sa.select(tokens_table.c.id, tokens_table.c.token)).fetchall()
    for row in rows:
        h = sha256(row.token.encode()).hexdigest()
        conn.execute(
            sa.update(tokens_table).where(tokens_table.c.id == row.id).values(token_hash=h)
        )

    op.alter_column('refresh_tokens', 'token_hash', nullable=False)

    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    op.drop_column('users', 'is_verified')
    op.drop_index(op.f('ix_refresh_tokens_token_hash'), table_name='refresh_tokens')
    op.drop_column('refresh_tokens', 'token_hash')
