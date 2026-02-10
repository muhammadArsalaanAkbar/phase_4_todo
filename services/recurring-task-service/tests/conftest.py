"""Shared test fixtures for Recurring Task Service tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.recurrence import RecurrenceSchedule


@pytest.fixture
def mock_session():
    """Create a mock async DB session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def sample_schedule():
    """Create a sample RecurrenceSchedule model instance."""
    now = datetime.now(timezone.utc)
    return RecurrenceSchedule(
        id=uuid.uuid4(),
        parent_task_id=uuid.uuid4(),
        frequency="daily",
        next_due_date=now,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
