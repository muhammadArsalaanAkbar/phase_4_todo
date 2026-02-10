"""Task: T050 — Notification SQLAlchemy model per data-model.md.

All fields from the Notification entity: UUID PK, task_id, notification_type,
channel, status, payload (JSONB), created_at, sent_at, error_message.
Indexes: idx_notifications_status, idx_notifications_task_id.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Notification(Base):
    """Notification model — tracks notification delivery status."""

    __tablename__ = "notifications"
    __table_args__ = (
        Index("idx_notifications_status", "status"),
        Index("idx_notifications_task_id", "task_id"),
        {"schema": "notification_service"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    notification_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    channel: Mapped[str] = mapped_column(
        String(20), nullable=False, default="in_app"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
