"""Task: T067 — Unit tests for scheduler jobs.

Tests schedule_reminder and publish_reminder with mocked Dapr client.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.scheduler import jobs


@pytest.mark.asyncio
@patch("app.scheduler.jobs.publish_event", new_callable=AsyncMock)
async def test_publish_reminder(mock_publish):
    """Test publishing a reminder event to the reminders topic."""
    task_id = str(uuid.uuid4())
    title = "Test reminder"
    reminder_time = datetime.now(timezone.utc).isoformat()

    await jobs.publish_reminder(task_id, title, reminder_time)

    mock_publish.assert_awaited_once()
    call_kwargs = mock_publish.call_args.kwargs
    assert call_kwargs["topic"] == "reminders"
    assert call_kwargs["event_type"] == "reminder-fired"
    assert call_kwargs["source"] == "recurring-task-service"


@pytest.mark.asyncio
@patch("app.scheduler.jobs.publish_event", new_callable=AsyncMock)
async def test_publish_reminder_event_structure(mock_publish):
    """Test that the reminder event has correct structure."""
    task_id = str(uuid.uuid4())
    title = "Buy groceries"
    reminder_time = "2026-02-10T12:00:00+00:00"

    await jobs.publish_reminder(task_id, title, reminder_time)

    event = mock_publish.call_args.kwargs["event"]
    assert str(event.task_id) == task_id
    assert event.event_type == "reminder-fired"
    assert event.payload.title == "Buy groceries"
    assert event.payload.channel == "in_app"


def test_schedule_reminder():
    """Test scheduling a reminder job."""
    # Start scheduler for the test
    jobs.start_scheduler()

    task_id = str(uuid.uuid4())
    title = "Scheduled task"
    future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()

    job_id = jobs.schedule_reminder(task_id, title, future_time)

    assert job_id is not None
    assert job_id == f"reminder-{task_id}"

    # Verify the job exists in the scheduler
    job = jobs.scheduler.get_job(job_id)
    assert job is not None

    # Clean up
    jobs.scheduler.remove_job(job_id)
    jobs.shutdown_scheduler()


def test_schedule_reminder_replaces_existing():
    """Test that scheduling replaces an existing reminder for the same task."""
    jobs.start_scheduler()

    task_id = str(uuid.uuid4())
    title = "Task with replacement"
    time1 = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    time2 = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()

    job_id1 = jobs.schedule_reminder(task_id, title, time1)
    job_id2 = jobs.schedule_reminder(task_id, title, time2)

    assert job_id1 == job_id2  # Same job ID

    # Only one job should exist
    all_jobs = jobs.scheduler.get_jobs()
    matching = [j for j in all_jobs if j.id == f"reminder-{task_id}"]
    assert len(matching) == 1

    # Clean up
    jobs.scheduler.remove_job(f"reminder-{task_id}")
    jobs.shutdown_scheduler()


def test_start_and_shutdown_scheduler():
    """Test scheduler start and shutdown lifecycle."""
    jobs.start_scheduler()
    assert jobs.scheduler.running is True

    jobs.shutdown_scheduler()
    assert jobs.scheduler.running is False


def test_start_scheduler_idempotent():
    """Test that starting an already-running scheduler is safe."""
    jobs.start_scheduler()
    jobs.start_scheduler()  # Should not raise
    assert jobs.scheduler.running is True

    jobs.shutdown_scheduler()
