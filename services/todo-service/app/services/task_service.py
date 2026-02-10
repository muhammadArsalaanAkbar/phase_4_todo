"""Task: T033 — TaskService business logic.

CRUD operations using async session. Publishes TaskEvent to task-events
and task-updates topics via shared dapr_helpers after each mutation.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.dapr_helpers import publish_event
from shared.events import TaskEvent, TaskPayload

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)

SOURCE_SERVICE = "todo-service"


def _build_task_event(task: Task, event_type: str) -> TaskEvent:
    """Build a TaskEvent from a Task model instance."""
    return TaskEvent(
        event_type=event_type,
        task_id=task.id,
        payload=TaskPayload(
            title=task.title,
            description=task.description,
            status=task.status,
            due_date=task.due_date,
            reminder_time=task.reminder_time,
            is_recurring=task.is_recurring,
            recurrence_schedule=task.recurrence_schedule,
        ),
    )


async def _publish_task_event(task: Task, event_type: str) -> None:
    """Publish a TaskEvent to both task-events and task-updates topics."""
    event = _build_task_event(task, event_type)
    await publish_event(
        topic="task-events", event=event, source=SOURCE_SERVICE, event_type=event_type
    )
    await publish_event(
        topic="task-updates", event=event, source=SOURCE_SERVICE, event_type=event_type
    )


async def create_task(session: AsyncSession, data: TaskCreate) -> Task:
    """Create a new task and publish task-created event."""
    task = Task(
        title=data.title,
        description=data.description,
        due_date=data.due_date,
        reminder_time=data.reminder_time,
        is_recurring=data.is_recurring,
        recurrence_schedule=(
            data.recurrence_schedule.value if data.recurrence_schedule else None
        ),
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    await _publish_task_event(task, "task-created")
    logger.info("Task created: %s", task.id, extra={"task_id": str(task.id)})
    return task


async def get_task(session: AsyncSession, task_id: uuid.UUID) -> Task | None:
    """Get a single task by ID."""
    result = await session.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def list_tasks(
    session: AsyncSession,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Task], int]:
    """List tasks with optional status filter, pagination."""
    query = select(Task)
    count_query = select(func.count()).select_from(Task)

    if status:
        query = query.where(Task.status == status)
        count_query = count_query.where(Task.status == status)

    query = query.order_by(Task.created_at.desc()).limit(limit).offset(offset)

    result = await session.execute(query)
    tasks = list(result.scalars().all())

    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    return tasks, total


async def update_task(
    session: AsyncSession, task_id: uuid.UUID, data: TaskUpdate
) -> Task | None:
    """Update a task and publish task-updated event."""
    task = await get_task(session, task_id)
    if not task:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "recurrence_schedule" and value is not None:
            value = value.value if hasattr(value, "value") else value
        if field == "status" and value is not None:
            value = value.value if hasattr(value, "value") else value
        setattr(task, field, value)

    await session.commit()
    await session.refresh(task)

    await _publish_task_event(task, "task-updated")
    logger.info("Task updated: %s", task.id, extra={"task_id": str(task.id)})
    return task


async def delete_task(session: AsyncSession, task_id: uuid.UUID) -> bool:
    """Delete a task and publish task-deleted event."""
    task = await get_task(session, task_id)
    if not task:
        return False

    event = _build_task_event(task, "task-deleted")
    await session.delete(task)
    await session.commit()

    await publish_event(
        topic="task-events", event=event, source=SOURCE_SERVICE, event_type="task-deleted"
    )
    await publish_event(
        topic="task-updates", event=event, source=SOURCE_SERVICE, event_type="task-deleted"
    )
    logger.info("Task deleted: %s", task_id, extra={"task_id": str(task_id)})
    return True


async def complete_task(session: AsyncSession, task_id: uuid.UUID) -> Task | None:
    """Mark a task as complete and publish task-completed event.

    Returns None if task not found, raises ValueError if already complete.
    """
    task = await get_task(session, task_id)
    if not task:
        return None

    if task.status == "complete":
        raise ValueError("Task is already completed")

    task.status = "complete"
    await session.commit()
    await session.refresh(task)

    await _publish_task_event(task, "task-completed")
    logger.info("Task completed: %s", task.id, extra={"task_id": str(task.id)})
    return task
