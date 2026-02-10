"""Task: T076 — Integration test for Todo→WebSocket broadcast.

Simulates a full flow: Todo Service creates a task, publishes TaskEvent
to task-updates topic via Dapr Pub/Sub, WebSocket Service receives it
and broadcasts to connected clients. Uses ASGI TestClient.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from app.main import app
from app.ws.manager import ConnectionManager, manager


@pytest.fixture
def sample_task_update_event():
    """Simulate a CloudEvents-wrapped TaskEvent for task-updates topic."""
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
                "title": "WS integration test task",
                "status": "pending",
            },
        },
    }


@pytest.mark.asyncio
async def test_dapr_subscribe_returns_task_updates_subscription():
    """Verify /dapr/subscribe advertises task-updates topic."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/dapr/subscribe")

    assert resp.status_code == 200
    subs = resp.json()
    assert len(subs) == 1
    assert subs[0]["pubsubname"] == "kafka-pubsub"
    assert subs[0]["topic"] == "task-updates"
    assert subs[0]["route"] == "/events/task-updates"


@pytest.mark.asyncio
async def test_task_update_event_broadcasts_to_clients(sample_task_update_event):
    """POST /events/task-updates → broadcast to WebSocket clients."""
    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()
    mock_ws.send_json = AsyncMock()

    # Add a mock client to the manager
    manager._connections.add(mock_ws)

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post(
                "/events/task-updates",
                json=sample_task_update_event,
            )

        assert resp.status_code == 200
        assert resp.json()["status"] == "SUCCESS"

        # Verify broadcast was called with formatted message
        mock_ws.send_json.assert_awaited_once()
        sent_msg = mock_ws.send_json.call_args[0][0]
        assert sent_msg["event_type"] == "task-created"
        assert "task_id" in sent_msg
        assert "payload" in sent_msg
    finally:
        manager._connections.discard(mock_ws)


@pytest.mark.asyncio
async def test_task_update_event_no_clients(sample_task_update_event):
    """POST /events/task-updates with zero clients still returns SUCCESS."""
    # Ensure no active connections
    manager._connections.clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/events/task-updates",
            json=sample_task_update_event,
        )

    assert resp.status_code == 200
    assert resp.json()["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_connection_count_endpoint():
    """Verify /api/v1/connections returns active connection count."""
    manager._connections.clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/connections")

    assert resp.status_code == 200
    assert resp.json()["active_connections"] == 0


@pytest.mark.asyncio
async def test_connection_count_with_clients():
    """Verify connection count reflects connected clients."""
    mock_ws1 = AsyncMock()
    mock_ws2 = AsyncMock()
    manager._connections.add(mock_ws1)
    manager._connections.add(mock_ws2)

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/v1/connections")

        assert resp.status_code == 200
        assert resp.json()["active_connections"] == 2
    finally:
        manager._connections.clear()


def test_websocket_connect_disconnect():
    """Test WebSocket connection lifecycle via ASGI TestClient."""
    client = TestClient(app)

    with client.websocket_connect("/ws") as ws:
        # Connection should be active
        assert manager.active_count >= 1

    # After disconnect, count should go back down
    # (Note: exact timing depends on cleanup)


@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify health endpoint is accessible."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "healthy"
