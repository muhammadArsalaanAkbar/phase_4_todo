"""Task: T031 — Create tasks table in todo_service schema.

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

SCHEMA = "todo_service"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "tasks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "status", sa.String(20), nullable=False, server_default="pending"
        ),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reminder_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_recurring", sa.Boolean, nullable=False, server_default="false"
        ),
        sa.Column("recurrence_schedule", sa.String(20), nullable=True),
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
        "idx_tasks_status", "tasks", ["status"], schema=SCHEMA
    )
    op.create_index(
        "idx_tasks_due_date", "tasks", ["due_date"], schema=SCHEMA
    )
    op.create_index(
        "idx_tasks_is_recurring", "tasks", ["is_recurring"], schema=SCHEMA
    )


def downgrade() -> None:
    op.drop_index("idx_tasks_is_recurring", table_name="tasks", schema=SCHEMA)
    op.drop_index("idx_tasks_due_date", table_name="tasks", schema=SCHEMA)
    op.drop_index("idx_tasks_status", table_name="tasks", schema=SCHEMA)
    op.drop_table("tasks", schema=SCHEMA)
