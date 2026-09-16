"""align userrole enum values with UserRole

The initial migration created `userrole` with UPPERCASE labels (USER/ADMIN/
MODERATOR) while the ORM writes the lowercase `UserRole` values, so a database
built purely from migrations rejected every user insert. Renaming the labels
aligns the type with `app.common.schemas.auth.UserRole`.

Idempotent: labels are only renamed when actually present, so the migration also
passes on databases created from `Base.metadata.create_all` (lowercase already).

Revision ID: b8c2d4e6f1a3
Revises: 7a1b2c3d4e5f
Create Date: 2026-10-01 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'b8c2d4e6f1a3'
down_revision: str | None = '7a1b2c3d4e5f'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


RENAMES = (('USER', 'user'), ('ADMIN', 'admin'), ('MODERATOR', 'moderator'))


def _labels() -> set[str]:
    rows = op.get_bind().execute(
        sa.text(
            "SELECT e.enumlabel FROM pg_type t JOIN pg_enum e ON e.enumtypid = t.oid WHERE t.typname = 'userrole'",
        ),
    )
    return set(rows.scalars())


def upgrade() -> None:
    labels = _labels()
    for old, new in RENAMES:
        if old in labels and new not in labels:
            op.execute(f"ALTER TYPE userrole RENAME VALUE '{old}' TO '{new}'")


def downgrade() -> None:
    labels = _labels()
    for old, new in RENAMES:
        if new in labels and old not in labels:
            op.execute(f"ALTER TYPE userrole RENAME VALUE '{new}' TO '{old}'")


__all__ = ['downgrade', 'revision', 'upgrade']
