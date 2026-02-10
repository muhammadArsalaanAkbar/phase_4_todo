"""Shared test fixtures for Todo Service tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.task import Task


@pytest.fixture
def mock_session():
    """Create a mock async DB session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def sample_task():
    """Create a sample Task model instance."""
    now = datetime.now(timezone.utc)
    task = Task(
        id=uuid.uuid4(),
        title="Test task",
        description="Test description",
        status="pending",
        due_date=None,
        reminder_time=None,
        is_recurring=False,
        recurrence_schedule=None,
        created_at=now,
        updated_at=now,
    )
    return task
