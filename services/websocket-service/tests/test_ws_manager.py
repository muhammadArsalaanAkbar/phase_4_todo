"""Task: T049 — Unit tests for ConnectionManager.

Tests connect, disconnect, broadcast to multiple clients,
and broadcast with zero clients.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ws.manager import ConnectionManager


@pytest.fixture
def mgr():
    """Create a fresh ConnectionManager for each test."""
    return ConnectionManager()


def _make_ws():
    """Create a mock WebSocket."""
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_connect(mgr):
    """Test connecting a WebSocket client."""
    ws = _make_ws()
    await mgr.connect(ws)

    assert mgr.active_count == 1
    ws.accept.assert_awaited_once()


@pytest.mark.asyncio
async def test_disconnect(mgr):
    """Test disconnecting a WebSocket client."""
    ws = _make_ws()
    await mgr.connect(ws)
    assert mgr.active_count == 1

    mgr.disconnect(ws)
    assert mgr.active_count == 0


@pytest.mark.asyncio
async def test_disconnect_not_connected(mgr):
    """Test disconnecting a client that was never connected."""
    ws = _make_ws()
    mgr.disconnect(ws)  # Should not raise
    assert mgr.active_count == 0


@pytest.mark.asyncio
async def test_broadcast_to_multiple_clients(mgr):
    """Test broadcasting a message to multiple clients."""
    ws1 = _make_ws()
    ws2 = _make_ws()
    ws3 = _make_ws()

    await mgr.connect(ws1)
    await mgr.connect(ws2)
    await mgr.connect(ws3)

    message = {"event_type": "task-created", "task_id": "abc-123"}
    await mgr.broadcast(message)

    ws1.send_json.assert_awaited_once_with(message)
    ws2.send_json.assert_awaited_once_with(message)
    ws3.send_json.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_broadcast_zero_clients(mgr):
    """Test broadcasting with no connected clients does nothing."""
    message = {"event_type": "task-created", "task_id": "abc-123"}
    await mgr.broadcast(message)  # Should not raise
    assert mgr.active_count == 0


@pytest.mark.asyncio
async def test_broadcast_removes_stale_clients(mgr):
    """Test that stale clients are removed during broadcast."""
    ws_good = _make_ws()
    ws_stale = _make_ws()
    ws_stale.send_json = AsyncMock(side_effect=Exception("Connection closed"))

    await mgr.connect(ws_good)
    await mgr.connect(ws_stale)
    assert mgr.active_count == 2

    message = {"event_type": "task-updated", "task_id": "xyz-789"}
    await mgr.broadcast(message)

    # Stale client should be removed
    assert mgr.active_count == 1
    ws_good.send_json.assert_awaited_once_with(message)


@pytest.mark.asyncio
async def test_multiple_connect_disconnect(mgr):
    """Test multiple connect/disconnect cycles."""
    ws1 = _make_ws()
    ws2 = _make_ws()

    await mgr.connect(ws1)
    await mgr.connect(ws2)
    assert mgr.active_count == 2

    mgr.disconnect(ws1)
    assert mgr.active_count == 1

    mgr.disconnect(ws2)
    assert mgr.active_count == 0


@pytest.mark.asyncio
async def test_broadcast_single_client(mgr):
    """Test broadcasting to exactly one client."""
    ws = _make_ws()
    await mgr.connect(ws)

    message = {"event_type": "task-deleted", "task_id": "del-123"}
    await mgr.broadcast(message)

    ws.send_json.assert_awaited_once_with(message)
    assert mgr.active_count == 1
