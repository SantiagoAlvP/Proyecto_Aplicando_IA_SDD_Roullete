"""add level to projects

Revision ID: c7d4e8f1a209
Revises: af53db99e207
Create Date: 2026-08-22 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c7d4e8f1a209"
down_revision: Union[str, Sequence[str], None] = "af53db99e207"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("level", sa.Integer(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE projects AS project
            SET level = LEAST(5, GREATEST(1, CAST(CEIL(extra_count / 2.0) AS INTEGER)))
            FROM (
                SELECT projects_id, COUNT(*) AS extra_count
                FROM project_extras
                GROUP BY projects_id
            ) AS counts
            WHERE project.id = counts.projects_id
            """
        )
    )
    op.execute(sa.text("UPDATE projects SET level = 1 WHERE level IS NULL"))
    op.alter_column("projects", "level", nullable=False, server_default="1")
    op.alter_column("projects", "level", server_default=None)


def downgrade() -> None:
    op.drop_column("projects", "level")
