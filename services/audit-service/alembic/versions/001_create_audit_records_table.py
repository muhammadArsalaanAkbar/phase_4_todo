"""Task: T039 — Create audit_records table.

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

SCHEMA = "audit_service"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "audit_records",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("event_id", UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("task_id", UUID(as_uuid=True), nullable=False),
        sa.Column("payload", JSONB, nullable=False),
        sa.Column("source_service", sa.String(100), nullable=False),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        schema=SCHEMA,
    )

    op.create_index(
        "idx_audit_task_id", "audit_records", ["task_id"], schema=SCHEMA
    )
    op.create_index(
        "idx_audit_event_type", "audit_records", ["event_type"], schema=SCHEMA
    )
    op.create_index(
        "idx_audit_recorded_at", "audit_records", ["recorded_at"], schema=SCHEMA
    )
    op.create_index(
        "idx_audit_event_id",
        "audit_records",
        ["event_id"],
        unique=True,
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_index("idx_audit_event_id", table_name="audit_records", schema=SCHEMA)
    op.drop_index("idx_audit_recorded_at", table_name="audit_records", schema=SCHEMA)
    op.drop_index("idx_audit_event_type", table_name="audit_records", schema=SCHEMA)
    op.drop_index("idx_audit_task_id", table_name="audit_records", schema=SCHEMA)
    op.drop_table("audit_records", schema=SCHEMA)
