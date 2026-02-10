"""Task: T075 — Integration test for Todo→Audit event pipeline.

Simulates a full flow: Todo Service creates a task, publishes TaskEvent
to task-events topic via Dapr Pub/Sub, Audit Service receives it and
stores an audit record. Uses mock DB and ASGI TestClient.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.audit_record import AuditRecord


@pytest.fixture
def sample_task_event():
    """Simulate a CloudEvents-wrapped TaskEvent as Dapr delivers it."""
    return {
        "specversion": "1.0",
        "type": "com.dapr.event.sent",
        "source": "todo-service",
        "id": str(uuid.uuid4()),
        "datacontenttype": "application/json",
        "data": {
            "event_id": str(uuid.uuid4()),
            "event_type": "task-created",
            "task_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "title": "Integration test task",
                "description": "Created via integration test",
                "status": "pending",
            },
            "source_service": "todo-service",
        },
    }


@pytest.fixture
def mock_audit_record(sample_task_event):
    """Create an AuditRecord matching the sample event."""
    data = sample_task_event["data"]
    return AuditRecord(
        id=uuid.uuid4(),
        event_id=uuid.UUID(data["event_id"]),
        event_type=data["event_type"],
        task_id=uuid.UUID(data["task_id"]),
        payload=data["payload"],
        source_service="todo-service",
        recorded_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_dapr_subscribe_returns_task_events_subscription():
    """Verify /dapr/subscribe advertises task-events topic."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/dapr/subscribe")

    assert resp.status_code == 200
    subs = resp.json()
    assert len(subs) == 1
    assert subs[0]["pubsubname"] == "kafka-pubsub"
    assert subs[0]["topic"] == "task-events"
    assert subs[0]["route"] == "/events/task-events"


@pytest.mark.asyncio
async def test_task_event_creates_audit_record(sample_task_event, mock_audit_record):
    """Full pipeline: POST /events/task-events → store_event → audit record."""
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.add = MagicMock()

    async def fake_refresh(obj):
        obj.id = mock_audit_record.id
        obj.recorded_at = mock_audit_record.recorded_at

    mock_session.refresh = AsyncMock(side_effect=fake_refresh)

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("app.events.handlers.async_session_factory", return_value=mock_ctx):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/events/task-events",
                json=sample_task_event,
            )

    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_duplicate_event_returns_success(sample_task_event):
    """Duplicate event (IntegrityError) still returns SUCCESS."""
    from sqlalchemy.exc import IntegrityError

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock(
        side_effect=IntegrityError("duplicate", {}, Exception())
    )
    mock_session.rollback = AsyncMock()

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("app.events.handlers.async_session_factory", return_value=mock_ctx):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/events/task-events",
                json=sample_task_event,
            )

    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"
    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_audit_query_after_event(sample_task_event, mock_audit_record):
    """Verify GET /api/v1/audit returns stored records."""
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_audit_record]
    mock_result_list = MagicMock()
    mock_result_list.scalars.return_value = mock_scalars

    mock_result_count = MagicMock()
    mock_result_count.scalar_one.return_value = 1

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(
        side_effect=[mock_result_list, mock_result_count]
    )

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_session)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("app.routers.audit.async_session_factory", return_value=mock_ctx):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/audit")

    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert len(body["records"]) == 1
    assert body["records"][0]["event_type"] == "task-created"


@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify health endpoint is accessible."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
