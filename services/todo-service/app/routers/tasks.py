"""Task: T034 — Tasks router per contracts/todo-service-api.yaml.

REST endpoints:
  GET    /api/v1/tasks                 — List tasks
  POST   /api/v1/tasks                 — Create task
  GET    /api/v1/tasks/{task_id}       — Get task
  PUT    /api/v1/tasks/{task_id}       — Update task
  DELETE /api/v1/tasks/{task_id}       — Delete task
  POST   /api/v1/tasks/{task_id}/complete — Complete task
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services import task_service

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: str | None = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> TaskListResponse:
    """List all tasks with optional status filter and pagination."""
    tasks, total = await task_service.list_tasks(session, status, limit, offset)
    return TaskListResponse(
        tasks=[TaskResponse.model_validate(t) for t in tasks],
        total=total,
    )


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    data: TaskCreate,
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Create a new task. Publishes task-created event."""
    task = await task_service.create_task(session, data)
    return TaskResponse.model_validate(task)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Get a task by ID."""
    task = await task_service.get_task(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Update a task. Publishes task-updated event."""
    task = await task_service.update_task(session, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> Response:
    """Delete a task. Publishes task-deleted event."""
    deleted = await task_service.delete_task(session, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """Mark a task as complete. Publishes task-completed event."""
    try:
        task = await task_service.complete_task(session, task_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)
