"""Task: T058 — RecurrenceSchedule SQLAlchemy model per data-model.md.

All fields: UUID PK, parent_task_id, frequency, next_due_date,
is_active, created_at, updated_at.
Indexes: idx_recurrence_parent_task, idx_recurrence_active_next.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RecurrenceSchedule(Base):
    """RecurrenceSchedule model — tracks recurring task patterns."""

    __tablename__ = "recurrence_schedules"
    __table_args__ = (
        Index("idx_recurrence_parent_task", "parent_task_id"),
        Index("idx_recurrence_active_next", "is_active", "next_due_date"),
        {"schema": "recurring_task_service"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    parent_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    next_due_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
