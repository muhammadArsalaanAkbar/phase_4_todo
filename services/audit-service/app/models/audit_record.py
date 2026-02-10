"""Task: T038 — AuditRecord SQLAlchemy model per data-model.md.

All fields from the AuditRecord entity: UUID PK, event_id (UNIQUE), event_type,
task_id, payload (JSONB), source_service, recorded_at.
Indexes: idx_audit_task_id, idx_audit_event_type, idx_audit_recorded_at,
idx_audit_event_id (UNIQUE).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AuditRecord(Base):
    """AuditRecord model — immutable log entry in the audit_service schema."""

    __tablename__ = "audit_records"
    __table_args__ = (
        Index("idx_audit_task_id", "task_id"),
        Index("idx_audit_event_type", "event_type"),
        Index("idx_audit_recorded_at", "recorded_at"),
        Index("idx_audit_event_id", "event_id", unique=True),
        {"schema": "audit_service"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    source_service: Mapped[str] = mapped_column(String(100), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
