"""HU-20: add share_token, level and created_at to projects

Retroactive scope (FR-007): every pre-existing project receives a permanent
public token generated in-process with `secrets.token_urlsafe(12)` (~96 bits,
D-01/D-05). Legacy difficulty levels stay NULL because they were never
persisted, and legacy creation dates fall back to the migration date
(documented assumption in data-model.md).

Revision ID: 3e7e9298a6c4
Revises: af53db99e207
Create Date: 2026-08-23

"""

from typing import Sequence, Union

import secrets

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3e7e9298a6c4"
down_revision: Union[str, Sequence[str], None] = "af53db99e207"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the public identity columns and backfill existing rows."""
    op.add_column(
        "projects",
        sa.Column("share_token", sa.String(length=64), nullable=True),
    )
    op.add_column("projects", sa.Column("level", sa.Integer(), nullable=True))
    op.add_column(
        "projects",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Backfill inside the migration so the feature ships with 100% of the
    # history shareable (SC-003). Parameterised statements only.
    conn = op.get_bind()
    rows = conn.execute(
        sa.text("SELECT id FROM projects WHERE share_token IS NULL")
    ).fetchall()
    for (project_id,) in rows:
        conn.execute(
            sa.text("UPDATE projects SET share_token = :token WHERE id = :id"),
            {"token": secrets.token_urlsafe(12), "id": project_id},
        )

    # The backfilled identity becomes permanent and unguessable-by-enumeration.
    op.alter_column(
        "projects", "share_token", existing_type=sa.String(length=64), nullable=False
    )
    op.create_index("ix_projects_share_token", "projects", ["share_token"], unique=True)


def downgrade() -> None:
    """Drop the public identity columns."""
    op.drop_index("ix_projects_share_token", table_name="projects")
    op.drop_column("projects", "created_at")
    op.drop_column("projects", "level")
    op.drop_column("projects", "share_token")
