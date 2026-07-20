"""use provider_name instead of provider_id FK

Revision ID: d4e5f6a7b8c9
Revises: a2b3c4d5e6f7
Create Date: 2026-07-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'a2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add provider_name column to task
    op.add_column('task', sa.Column('provider_name', sa.String(length=100), nullable=False, server_default=''))
    op.create_index(op.f('ix_task_provider_name'), 'task', ['provider_name'])

    # Add provider_name column to request_log
    op.add_column('request_log', sa.Column('provider_name', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_request_log_provider_name'), 'request_log', ['provider_name'])

    # Backfill provider_name from provider records where possible
    op.execute("""
        UPDATE task
        SET provider_name = COALESCE(
            (SELECT name FROM provider WHERE provider.id = task.provider_id),
            'unknown'
        )
    """)
    op.execute("""
        UPDATE request_log
        SET provider_name = (
            SELECT name FROM provider WHERE provider.id = request_log.provider_id
        )
    """)

    # Drop old FK columns
    op.drop_index('ix_task_provider_id', table_name='task')
    op.drop_constraint('task_provider_id_fkey', 'task', type_='foreignkey')
    op.drop_column('task', 'provider_id')

    op.drop_index('ix_request_log_provider_id', table_name='request_log')
    op.drop_constraint('request_log_provider_id_fkey', 'request_log', type_='foreignkey')
    op.drop_column('request_log', 'provider_id')


def downgrade() -> None:
    # Restore provider_id FK columns
    op.add_column('request_log', sa.Column('provider_id', sa.Integer(), nullable=True))
    op.create_index('ix_request_log_provider_id', 'request_log', ['provider_id'])
    op.create_foreign_key('request_log_provider_id_fkey', 'request_log', 'provider', ['provider_id'], ['id'], ondelete='CASCADE')

    op.add_column('task', sa.Column('provider_id', sa.Integer(), nullable=False, server_default='0'))
    op.create_index('ix_task_provider_id', 'task', ['provider_id'])
    op.create_foreign_key('task_provider_id_fkey', 'task', 'provider', ['provider_id'], ['id'], ondelete='CASCADE')

    # Backfill provider_id
    op.execute("""
        UPDATE task
        SET provider_id = COALESCE(
            (SELECT id FROM provider WHERE provider.name = task.provider_name),
            0
        )
    """)
    op.execute("""
        UPDATE request_log
        SET provider_id = (
            SELECT id FROM provider WHERE provider.name = request_log.provider_name
        )
    """)

    op.drop_index(op.f('ix_task_provider_name'), table_name='task')
    op.drop_column('task', 'provider_name')

    op.drop_index(op.f('ix_request_log_provider_name'), table_name='request_log')
    op.drop_column('request_log', 'provider_name')
