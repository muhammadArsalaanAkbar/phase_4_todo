"""Task: T036 — Unit tests for TaskService.

Tests create, update, delete, complete with mocked DB session and
mocked Dapr client (publish_event).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import task_service


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
    return Task(
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


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_create_task(mock_publish, mock_session):
    """Test creating a task publishes task-created event."""
    data = TaskCreate(title="New task", description="Details")

    # Mock refresh to set id and timestamps
    async def fake_refresh(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.now(timezone.utc)
        obj.updated_at = datetime.now(timezone.utc)

    mock_session.refresh = AsyncMock(side_effect=fake_refresh)

    result = await task_service.create_task(mock_session, data)

    assert result.title == "New task"
    assert result.description == "Details"
    assert result.status == "pending"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    # Published to both task-events and task-updates
    assert mock_publish.await_count == 2
    call_topics = [call.kwargs["topic"] for call in mock_publish.call_args_list]
    assert "task-events" in call_topics
    assert "task-updates" in call_topics


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_update_task(mock_publish, mock_session, sample_task):
    """Test updating a task publishes task-updated event."""
    # Mock get_task to return sample_task
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_task
    mock_session.execute = AsyncMock(return_value=mock_result)

    data = TaskUpdate(title="Updated title")
    result = await task_service.update_task(mock_session, sample_task.id, data)

    assert result is not None
    assert result.title == "Updated title"
    mock_session.commit.assert_awaited_once()
    assert mock_publish.await_count == 2


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_update_task_not_found(mock_publish, mock_session):
    """Test updating a non-existent task returns None."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    data = TaskUpdate(title="Updated title")
    result = await task_service.update_task(mock_session, uuid.uuid4(), data)

    assert result is None
    mock_publish.assert_not_awaited()


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_delete_task(mock_publish, mock_session, sample_task):
    """Test deleting a task publishes task-deleted event."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_task
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await task_service.delete_task(mock_session, sample_task.id)

    assert result is True
    mock_session.delete.assert_awaited_once_with(sample_task)
    mock_session.commit.assert_awaited_once()
    assert mock_publish.await_count == 2


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_delete_task_not_found(mock_publish, mock_session):
    """Test deleting a non-existent task returns False."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await task_service.delete_task(mock_session, uuid.uuid4())

    assert result is False
    mock_publish.assert_not_awaited()


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_complete_task(mock_publish, mock_session, sample_task):
    """Test completing a task publishes task-completed event."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_task
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await task_service.complete_task(mock_session, sample_task.id)

    assert result is not None
    assert result.status == "complete"
    mock_session.commit.assert_awaited_once()
    assert mock_publish.await_count == 2


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_complete_task_already_completed(mock_publish, mock_session, sample_task):
    """Test completing an already-completed task raises ValueError."""
    sample_task.status = "complete"
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_task
    mock_session.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(ValueError, match="already completed"):
        await task_service.complete_task(mock_session, sample_task.id)

    mock_publish.assert_not_awaited()


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_complete_task_not_found(mock_publish, mock_session):
    """Test completing a non-existent task returns None."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await task_service.complete_task(mock_session, uuid.uuid4())

    assert result is None
    mock_publish.assert_not_awaited()
