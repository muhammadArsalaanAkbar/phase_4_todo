"""Task: T037 — API endpoint tests for Todo Service.

Tests all 6 endpoints using httpx AsyncClient with FastAPI TestClient.
Mocks DB session and Dapr publish_event for isolation.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import get_session
from app.main import app
from app.models.task import Task

TASK_ID = uuid.uuid4()
NOW = datetime.now(timezone.utc)


def _make_task(**overrides) -> Task:
    """Create a Task instance with defaults."""
    defaults = {
        "id": TASK_ID,
        "title": "Test task",
        "description": "Test description",
        "status": "pending",
        "due_date": None,
        "reminder_time": None,
        "is_recurring": False,
        "recurrence_schedule": None,
        "created_at": NOW,
        "updated_at": NOW,
    }
    defaults.update(overrides)
    return Task(**defaults)


@pytest.fixture
def mock_session():
    """Provide a mock async session via DI override."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.add = MagicMock()

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield session
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    """Create async test client."""
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_create_task(mock_publish, mock_session, client):
    """POST /api/v1/tasks — 201 Created."""
    async def fake_refresh(obj):
        obj.id = TASK_ID
        obj.created_at = NOW
        obj.updated_at = NOW

    mock_session.refresh = AsyncMock(side_effect=fake_refresh)

    async with client:
        response = await client.post(
            "/api/v1/tasks",
            json={"title": "Test task", "description": "Test description"},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["status"] == "pending"
    assert data["id"] == str(TASK_ID)


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_list_tasks(mock_publish, mock_session, client):
    """GET /api/v1/tasks — 200 OK."""
    task = _make_task()
    # Mock for list query
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [task]
    mock_result_list = MagicMock()
    mock_result_list.scalars.return_value = mock_scalars
    # Mock for count query
    mock_result_count = MagicMock()
    mock_result_count.scalar_one.return_value = 1

    mock_session.execute = AsyncMock(
        side_effect=[mock_result_list, mock_result_count]
    )

    async with client:
        response = await client.get("/api/v1/tasks")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["title"] == "Test task"


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_get_task(mock_publish, mock_session, client):
    """GET /api/v1/tasks/{task_id} — 200 OK."""
    task = _make_task()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = task
    mock_session.execute = AsyncMock(return_value=mock_result)

    async with client:
        response = await client.get(f"/api/v1/tasks/{TASK_ID}")

    assert response.status_code == 200
    assert response.json()["id"] == str(TASK_ID)


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_get_task_not_found(mock_publish, mock_session, client):
    """GET /api/v1/tasks/{task_id} — 404 Not Found."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    async with client:
        response = await client.get(f"/api/v1/tasks/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_update_task(mock_publish, mock_session, client):
    """PUT /api/v1/tasks/{task_id} — 200 OK."""
    task = _make_task()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = task
    mock_session.execute = AsyncMock(return_value=mock_result)

    async with client:
        response = await client.put(
            f"/api/v1/tasks/{TASK_ID}",
            json={"title": "Updated title"},
        )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_delete_task(mock_publish, mock_session, client):
    """DELETE /api/v1/tasks/{task_id} — 204 No Content."""
    task = _make_task()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = task
    mock_session.execute = AsyncMock(return_value=mock_result)

    async with client:
        response = await client.delete(f"/api/v1/tasks/{TASK_ID}")

    assert response.status_code == 204


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_complete_task(mock_publish, mock_session, client):
    """POST /api/v1/tasks/{task_id}/complete — 200 OK."""
    task = _make_task(status="pending")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = task
    mock_session.execute = AsyncMock(return_value=mock_result)

    async with client:
        response = await client.post(f"/api/v1/tasks/{TASK_ID}/complete")

    assert response.status_code == 200
    assert response.json()["status"] == "complete"


@pytest.mark.asyncio
@patch("app.services.task_service.publish_event", new_callable=AsyncMock)
async def test_complete_task_already_completed(mock_publish, mock_session, client):
    """POST /api/v1/tasks/{task_id}/complete — 409 Conflict."""
    task = _make_task(status="complete")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = task
    mock_session.execute = AsyncMock(return_value=mock_result)

    async with client:
        response = await client.post(f"/api/v1/tasks/{TASK_ID}/complete")

    assert response.status_code == 409
