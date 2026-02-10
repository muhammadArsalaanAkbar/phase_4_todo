"""Task: T059 — Create recurrence_schedules table.

Revision ID: 001
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "recurring_task_service"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "recurrence_schedules",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("parent_task_id", UUID(as_uuid=True), nullable=False),
        sa.Column("frequency", sa.String(20), nullable=False),
        sa.Column("next_due_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "is_active", sa.Boolean, nullable=False, server_default=sa.true()
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        schema=SCHEMA,
    )

    op.create_index(
        "idx_recurrence_parent_task",
        "recurrence_schedules",
        ["parent_task_id"],
        schema=SCHEMA,
    )
    op.create_index(
        "idx_recurrence_active_next",
        "recurrence_schedules",
        ["is_active", "next_due_date"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_recurrence_active_next",
        table_name="recurrence_schedules",
        schema=SCHEMA,
    )
    op.drop_index(
        "idx_recurrence_parent_task",
        table_name="recurrence_schedules",
        schema=SCHEMA,
    )
    op.drop_table("recurrence_schedules", schema=SCHEMA)
