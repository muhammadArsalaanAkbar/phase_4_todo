"""Shared test fixtures for Notification Service tests."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.notification import Notification


@pytest.fixture
def mock_session():
    """Create a mock async DB session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def sample_notification():
    """Create a sample Notification model instance."""
    now = datetime.now(timezone.utc)
    return Notification(
        id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        notification_type="reminder",
        channel="in_app",
        status="pending",
        payload={"title": "Test reminder", "reminder_time": now.isoformat()},
        created_at=now,
        sent_at=None,
        error_message=None,
    )
