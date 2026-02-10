"""Shared test fixtures for Audit Service tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.audit_record import AuditRecord


@pytest.fixture
def mock_session():
    """Create a mock async DB session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def sample_audit_record():
    """Create a sample AuditRecord model instance."""
    now = datetime.now(timezone.utc)
    return AuditRecord(
        id=uuid.uuid4(),
        event_id=uuid.uuid4(),
        event_type="task-created",
        task_id=uuid.uuid4(),
        payload={"title": "Test task", "status": "pending"},
        source_service="todo-service",
        recorded_at=now,
    )
