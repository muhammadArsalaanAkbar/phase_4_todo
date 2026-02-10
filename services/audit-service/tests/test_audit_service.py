"""Task: T045 — Unit tests for AuditService.

Tests store_event, idempotency (duplicate event_id), list/filter queries,
and get_record.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.audit_record import AuditRecord
from app.services import audit_service


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
def sample_record():
    """Create a sample AuditRecord."""
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


@pytest.mark.asyncio
async def test_store_event(mock_session):
    """Test storing a new audit record."""
    event_id = uuid.uuid4()
    task_id = uuid.uuid4()

    async def fake_refresh(obj):
        obj.id = uuid.uuid4()
        obj.recorded_at = datetime.now(timezone.utc)

    mock_session.refresh = AsyncMock(side_effect=fake_refresh)

    result = await audit_service.store_event(
        session=mock_session,
        event_id=event_id,
        event_type="task-created",
        task_id=task_id,
        payload={"title": "Test"},
        source_service="todo-service",
    )

    assert result is not None
    assert result.event_type == "task-created"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_store_event_duplicate(mock_session):
    """Test idempotency — duplicate event_id returns None."""
    mock_session.commit = AsyncMock(
        side_effect=IntegrityError("duplicate", {}, Exception())
    )

    result = await audit_service.store_event(
        session=mock_session,
        event_id=uuid.uuid4(),
        event_type="task-created",
        task_id=uuid.uuid4(),
        payload={"title": "Test"},
        source_service="todo-service",
    )

    assert result is None
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_records(mock_session, sample_record):
    """Test listing audit records."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sample_record]
    mock_result_list = MagicMock()
    mock_result_list.scalars.return_value = mock_scalars

    mock_result_count = MagicMock()
    mock_result_count.scalar_one.return_value = 1

    mock_session.execute = AsyncMock(
        side_effect=[mock_result_list, mock_result_count]
    )

    records, total = await audit_service.list_records(mock_session)

    assert total == 1
    assert len(records) == 1
    assert records[0].event_type == "task-created"


@pytest.mark.asyncio
async def test_list_records_with_task_id_filter(mock_session, sample_record):
    """Test listing audit records filtered by task_id."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sample_record]
    mock_result_list = MagicMock()
    mock_result_list.scalars.return_value = mock_scalars

    mock_result_count = MagicMock()
    mock_result_count.scalar_one.return_value = 1

    mock_session.execute = AsyncMock(
        side_effect=[mock_result_list, mock_result_count]
    )

    records, total = await audit_service.list_records(
        mock_session, task_id=sample_record.task_id
    )

    assert total == 1
    assert len(records) == 1


@pytest.mark.asyncio
async def test_list_records_with_event_type_filter(mock_session, sample_record):
    """Test listing audit records filtered by event_type."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [sample_record]
    mock_result_list = MagicMock()
    mock_result_list.scalars.return_value = mock_scalars

    mock_result_count = MagicMock()
    mock_result_count.scalar_one.return_value = 1

    mock_session.execute = AsyncMock(
        side_effect=[mock_result_list, mock_result_count]
    )

    records, total = await audit_service.list_records(
        mock_session, event_type="task-created"
    )

    assert total == 1
    assert len(records) == 1


@pytest.mark.asyncio
async def test_get_record(mock_session, sample_record):
    """Test getting a single audit record by ID."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = sample_record
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await audit_service.get_record(mock_session, sample_record.id)

    assert result is not None
    assert result.id == sample_record.id


@pytest.mark.asyncio
async def test_get_record_not_found(mock_session):
    """Test getting a non-existent audit record returns None."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await audit_service.get_record(mock_session, uuid.uuid4())

    assert result is None


@pytest.mark.asyncio
async def test_list_records_empty(mock_session):
    """Test listing when no records exist."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []
    mock_result_list = MagicMock()
    mock_result_list.scalars.return_value = mock_scalars

    mock_result_count = MagicMock()
    mock_result_count.scalar_one.return_value = 0

    mock_session.execute = AsyncMock(
        side_effect=[mock_result_list, mock_result_count]
    )

    records, total = await audit_service.list_records(mock_session)

    assert total == 0
    assert len(records) == 0
