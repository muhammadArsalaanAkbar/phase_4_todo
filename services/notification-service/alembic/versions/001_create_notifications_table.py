"""Task: T051 — Create notifications table.

Revision ID: 001
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "001"
down_revision = None
branch_labels = None
depends_on = None

SCHEMA = "notification_service"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "notifications",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("task_id", UUID(as_uuid=True), nullable=False),
        sa.Column("notification_type", sa.String(20), nullable=False),
        sa.Column(
            "channel",
            sa.String(20),
            nullable=False,
            server_default="in_app",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("payload", JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        schema=SCHEMA,
    )

    op.create_index(
        "idx_notifications_status",
        "notifications",
        ["status"],
        schema=SCHEMA,
    )
    op.create_index(
        "idx_notifications_task_id",
        "notifications",
        ["task_id"],
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "idx_notifications_task_id",
        table_name="notifications",
        schema=SCHEMA,
    )
    op.drop_index(
        "idx_notifications_status",
        table_name="notifications",
        schema=SCHEMA,
    )
    op.drop_table("notifications", schema=SCHEMA)
