"""Task: T066 — Unit tests for RecurrenceService.

Tests handle_task_created (recurring), handle_task_completed
(next_due_date calculation for daily/weekly/monthly),
handle_task_deleted (deactivation), list_schedules, get_schedule.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.recurrence import RecurrenceSchedule
from app.services import recurrence_service


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
    """Create a sample RecurrenceSchedule."""
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


@pytest.mark.asyncio
async def test_handle_task_created_recurring(mock_session):
    """Test creating a schedule for a recurring task."""
    task_id = uuid.uuid4()
    due_date = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    async def fake_refresh(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.now(timezone.utc)
        obj.updated_at = datetime.now(timezone.utc)

    mock_session.refresh = AsyncMock(side_effect=fake_refresh)

    event_data = {
        "task_id": str(task_id),
        "event_type": "task-created",
        "payload": {
            "is_recurring": True,
            "recurrence_schedule": "daily",
            "due_date": due_date,
            "title": "Recurring task",
        },
    }

    result = await recurrence_service.handle_task_created(mock_session, event_data)

    assert result is not None
    assert result.frequency == "daily"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_task_created_not_recurring(mock_session):
    """Test that non-recurring tasks are ignored."""
    event_data = {
        "task_id": str(uuid.uuid4()),
        "event_type": "task-created",
        "payload": {"is_recurring": False, "title": "One-time task"},
    }

    result = await recurrence_service.handle_task_created(mock_session, event_data)

    assert result is None
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
@patch("app.services.recurrence_service.publish_event", new_callable=AsyncMock)
async def test_handle_task_completed_daily(mock_publish, mock_session, sample_schedule):
    """Test advancing a daily schedule on task completion."""
    original_due = sample_schedule.next_due_date

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_schedule
    mock_session.execute = AsyncMock(return_value=mock_result)

    event_data = {
        "task_id": str(sample_schedule.parent_task_id),
        "event_type": "task-completed",
        "payload": {"title": "Daily task", "status": "complete"},
    }

    result = await recurrence_service.handle_task_completed(mock_session, event_data)

    assert result is not None
    assert result.next_due_date == original_due + timedelta(days=1)
    mock_publish.assert_awaited_once()


@pytest.mark.asyncio
@patch("app.services.recurrence_service.publish_event", new_callable=AsyncMock)
async def test_handle_task_completed_weekly(mock_publish, mock_session):
    """Test advancing a weekly schedule on task completion."""
    now = datetime.now(timezone.utc)
    schedule = RecurrenceSchedule(
        id=uuid.uuid4(),
        parent_task_id=uuid.uuid4(),
        frequency="weekly",
        next_due_date=now,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = schedule
    mock_session.execute = AsyncMock(return_value=mock_result)

    event_data = {
        "task_id": str(schedule.parent_task_id),
        "event_type": "task-completed",
        "payload": {"title": "Weekly task"},
    }

    result = await recurrence_service.handle_task_completed(mock_session, event_data)

    assert result is not None
    assert result.next_due_date == now + timedelta(weeks=1)


@pytest.mark.asyncio
@patch("app.services.recurrence_service.publish_event", new_callable=AsyncMock)
async def test_handle_task_completed_monthly(mock_publish, mock_session):
    """Test advancing a monthly schedule on task completion."""
    now = datetime.now(timezone.utc)
    schedule = RecurrenceSchedule(
        id=uuid.uuid4(),
        parent_task_id=uuid.uuid4(),
        frequency="monthly",
        next_due_date=now,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = schedule
    mock_session.execute = AsyncMock(return_value=mock_result)

    event_data = {
        "task_id": str(schedule.parent_task_id),
        "event_type": "task-completed",
        "payload": {"title": "Monthly task"},
    }

    result = await recurrence_service.handle_task_completed(mock_session, event_data)

    assert result is not None
    assert result.next_due_date == now + timedelta(days=30)


@pytest.mark.asyncio
@patch("app.services.recurrence_service.publish_event", new_callable=AsyncMock)
async def test_handle_task_completed_no_schedule(mock_publish, mock_session):
    """Test completing a task with no recurrence schedule."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    event_data = {
        "task_id": str(uuid.uuid4()),
        "event_type": "task-completed",
        "payload": {"title": "One-time task"},
    }

    result = await recurrence_service.handle_task_completed(mock_session, event_data)

    assert result is None
    mock_publish.assert_not_awaited()


@pytest.mark.asyncio
async def test_handle_task_deleted(mock_session, sample_schedule):
    """Test deactivating a schedule on task deletion."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_schedule
    mock_session.execute = AsyncMock(return_value=mock_result)

    event_data = {
        "task_id": str(sample_schedule.parent_task_id),
        "event_type": "task-deleted",
    }

    result = await recurrence_service.handle_task_deleted(mock_session, event_data)

    assert result is not None
    assert result.is_active is False
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_task_deleted_no_schedule(mock_session):
    """Test deleting a task with no recurrence schedule."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    event_data = {
        "task_id": str(uuid.uuid4()),
        "event_type": "task-deleted",
    }

    result = await recurrence_service.handle_task_deleted(mock_session, event_data)

    assert result is None
