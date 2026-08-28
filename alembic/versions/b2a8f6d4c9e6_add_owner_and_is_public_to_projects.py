"""add owner_id, owner_name and is_public to projects

Revision ID: b2a8f6d4c9e6
Revises: c19f2a7b3d41
Create Date: 2026-08-28 15:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b2a8f6d4c9e6"
down_revision: Union[str, Sequence[str], None] = "c19f2a7b3d41"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add owner_id, owner_name, is_public to projects."""
    op.add_column(
        "projects",
        sa.Column("owner_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("owner_name", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "projects",
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    """Downgrade schema: remove owner_id, owner_name, is_public from projects."""
    op.drop_column("projects", "is_public")
    op.drop_column("projects", "owner_name")
    op.drop_column("projects", "owner_id")
