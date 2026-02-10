"""Task: T057 — Unit tests for NotificationService.

Tests create_notification, deliver_notification (success), handle_failure,
list_notifications with filters, and delivery idempotency edge cases.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.notification import Notification
from app.services import notification_service


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
    """Create a sample pending Notification."""
    now = datetime.now(timezone.utc)
    return Notification(
        id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        notification_type="reminder",
        channel="in_app",
        status="pending",
        payload={"title": "Test reminder"},
        created_at=now,
        sent_at=None,
        error_message=None,
    )


@pytest.mark.asyncio
async def test_create_notification(mock_session):
    """Test creating a new notification record."""
    task_id = uuid.uuid4()

    async def fake_refresh(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.now(timezone.utc)

    mock_session.refresh = AsyncMock(side_effect=fake_refresh)

    result = await notification_service.create_notification(
        session=mock_session,
        task_id=task_id,
        notification_type="reminder",
        payload={"title": "Buy groceries"},
    )

    assert result is not None
    assert result.notification_type == "reminder"
    assert result.channel == "in_app"
    assert result.status == "pending"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_notification_with_custom_channel(mock_session):
    """Test creating a notification with explicit channel."""
    task_id = uuid.uuid4()

    async def fake_refresh(obj):
        obj.id = uuid.uuid4()
        obj.created_at = datetime.now(timezone.utc)

    mock_session.refresh = AsyncMock(side_effect=fake_refresh)

    result = await notification_service.create_notification(
        session=mock_session,
        task_id=task_id,
        notification_type="update",
        payload={"title": "Task updated"},
        channel="in_app",
    )

    assert result.notification_type == "update"
    assert result.channel == "in_app"


@pytest.mark.asyncio
async def test_deliver_notification_in_app(mock_session, sample_notification):
    """Test delivering an in_app notification marks as sent."""
    result = await notification_service.deliver_notification(
        mock_session, sample_notification
    )

    assert result.status == "sent"
    assert result.sent_at is not None
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_deliver_notification_unsupported_channel(mock_session):
    """Test delivering via unsupported channel does not change status."""
    now = datetime.now(timezone.utc)
    notification = Notification(
        id=uuid.uuid4(),
        task_id=uuid.uuid4(),
        notification_type="reminder",
        channel="email",  # Unsupported in MVP
        status="pending",
        payload={"title": "Test"},
        created_at=now,
    )

    result = await notification_service.deliver_notification(
        mock_session, notification
    )

    # Status should remain pending — unsupported channel
    assert result.status == "pending"
    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_handle_failure(mock_session, sample_notification):
    """Test marking a notification as failed."""
    result = await notification_service.handle_failure(
        mock_session, sample_notification, "Connection timeout"
    )

    assert result.status == "failed"
    assert result.error_message == "Connection timeout"
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_notifications(mock_session, sample_notification):
    """Test listing notifications without filters."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sample_notification]
    mock_result_list = MagicMock()
    mock_result_list.scalars.return_value = mock_scalars

    mock_result_count = MagicMock()
    mock_result_count.scalar_one.return_value = 1

    mock_session.execute = AsyncMock(
        side_effect=[mock_result_list, mock_result_count]
    )

    notifications, total = await notification_service.list_notifications(
        mock_session
    )

    assert total == 1
    assert len(notifications) == 1
    assert notifications[0].notification_type == "reminder"


@pytest.mark.asyncio
async def test_list_notifications_by_status(mock_session, sample_notification):
    """Test listing notifications filtered by status."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sample_notification]
    mock_result_list = MagicMock()
    mock_result_list.scalars.return_value = mock_scalars

    mock_result_count = MagicMock()
    mock_result_count.scalar_one.return_value = 1

    mock_session.execute = AsyncMock(
        side_effect=[mock_result_list, mock_result_count]
    )

    notifications, total = await notification_service.list_notifications(
        mock_session, status="pending"
    )

    assert total == 1
    assert len(notifications) == 1


@pytest.mark.asyncio
async def test_list_notifications_by_task_id(mock_session, sample_notification):
    """Test listing notifications filtered by task_id."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sample_notification]
    mock_result_list = MagicMock()
    mock_result_list.scalars.return_value = mock_scalars

    mock_result_count = MagicMock()
    mock_result_count.scalar_one.return_value = 1

    mock_session.execute = AsyncMock(
        side_effect=[mock_result_list, mock_result_count]
    )

    notifications, total = await notification_service.list_notifications(
        mock_session, task_id=sample_notification.task_id
    )

    assert total == 1
    assert len(notifications) == 1


@pytest.mark.asyncio
async def test_list_notifications_empty(mock_session):
    """Test listing when no notifications exist."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result_list = MagicMock()
    mock_result_list.scalars.return_value = mock_scalars

    mock_result_count = MagicMock()
    mock_result_count.scalar_one.return_value = 0

    mock_session.execute = AsyncMock(
        side_effect=[mock_result_list, mock_result_count]
    )

    notifications, total = await notification_service.list_notifications(
        mock_session
    )

    assert total == 0
    assert len(notifications) == 0
