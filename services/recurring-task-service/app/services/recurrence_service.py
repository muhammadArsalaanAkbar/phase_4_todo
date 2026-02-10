"""Task: T061 — RecurrenceService business logic.

handle_task_created (create schedule if is_recurring),
handle_task_completed (calculate next_due_date, publish new task via Dapr),
handle_task_deleted (deactivate schedule), list_schedules, get_schedule.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.dapr_helpers import publish_event
from shared.events import TaskEvent, TaskPayload

from app.models.recurrence import RecurrenceSchedule

logger = logging.getLogger(__name__)

SOURCE_SERVICE = "recurring-task-service"

# Frequency to timedelta mapping
FREQUENCY_DELTAS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "monthly": timedelta(days=30),  # Approximate
}


def _calculate_next_due_date(frequency: str, current_due: datetime) -> datetime:
    """Calculate the next due date based on frequency."""
    delta = FREQUENCY_DELTAS.get(frequency, timedelta(days=1))
    return current_due + delta


async def handle_task_created(
    session: AsyncSession, event_data: dict
) -> RecurrenceSchedule | None:
    """Handle task-created event. Create a schedule if the task is recurring."""
    payload = event_data.get("payload", {})
    if not payload.get("is_recurring"):
        return None

    task_id = uuid.UUID(str(event_data["task_id"]))
    frequency = payload.get("recurrence_schedule", "daily")
    due_date = payload.get("due_date")

    if due_date:
        if isinstance(due_date, str):
            next_due = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        else:
            next_due = due_date
    else:
        next_due = datetime.now(timezone.utc) + FREQUENCY_DELTAS.get(
            frequency, timedelta(days=1)
        )

    schedule = RecurrenceSchedule(
        parent_task_id=task_id,
        frequency=frequency,
        next_due_date=next_due,
    )
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)

    logger.info(
        "Recurrence schedule created: %s for task %s (%s)",
        schedule.id,
        task_id,
        frequency,
    )
    return schedule


async def handle_task_completed(
    session: AsyncSession, event_data: dict
) -> RecurrenceSchedule | None:
    """Handle task-completed event. Calculate next due date and publish new task."""
    task_id = uuid.UUID(str(event_data["task_id"]))

    result = await session.execute(
        select(RecurrenceSchedule).where(
            RecurrenceSchedule.parent_task_id == task_id,
            RecurrenceSchedule.is_active == True,  # noqa: E712
        )
    )
    schedule = result.scalar_one_or_none()

    if not schedule:
        return None

    # Calculate next due date
    schedule.next_due_date = _calculate_next_due_date(
        schedule.frequency, schedule.next_due_date
    )
    await session.commit()
    await session.refresh(schedule)

    # Publish a new task creation event to task-events
    payload = event_data.get("payload", {})
    new_task_event = TaskEvent(
        event_type="task-created",
        task_id=uuid.uuid4(),  # New task instance
        payload=TaskPayload(
            title=payload.get("title", "Recurring task"),
            description=payload.get("description"),
            status="pending",
            due_date=schedule.next_due_date,
            reminder_time=payload.get("reminder_time"),
            is_recurring=True,
            recurrence_schedule=schedule.frequency,
        ),
    )

    await publish_event(
        topic="task-events",
        event=new_task_event,
        source=SOURCE_SERVICE,
        event_type="task-created",
    )

    logger.info(
        "Recurrence advanced: schedule %s, next due %s",
        schedule.id,
        schedule.next_due_date,
    )
    return schedule


async def handle_task_deleted(
    session: AsyncSession, event_data: dict
) -> RecurrenceSchedule | None:
    """Handle task-deleted event. Deactivate the recurrence schedule."""
    task_id = uuid.UUID(str(event_data["task_id"]))

    result = await session.execute(
        select(RecurrenceSchedule).where(
            RecurrenceSchedule.parent_task_id == task_id,
            RecurrenceSchedule.is_active == True,  # noqa: E712
        )
    )
    schedule = result.scalar_one_or_none()

    if not schedule:
        return None

    schedule.is_active = False
    await session.commit()
    await session.refresh(schedule)

    logger.info("Recurrence deactivated: schedule %s", schedule.id)
    return schedule


async def list_schedules(
    session: AsyncSession,
    is_active: bool | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[RecurrenceSchedule], int]:
    """List recurrence schedules with optional is_active filter."""
    query = select(RecurrenceSchedule)
    count_query = select(func.count()).select_from(RecurrenceSchedule)

    if is_active is not None:
        query = query.where(RecurrenceSchedule.is_active == is_active)
        count_query = count_query.where(RecurrenceSchedule.is_active == is_active)

    query = query.order_by(RecurrenceSchedule.created_at.desc()).limit(limit).offset(offset)

    result = await session.execute(query)
    schedules = list(result.scalars().all())

    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    return schedules, total


async def get_schedule(
    session: AsyncSession, schedule_id: uuid.UUID
) -> RecurrenceSchedule | None:
    """Get a single recurrence schedule by ID."""
    result = await session.execute(
        select(RecurrenceSchedule).where(RecurrenceSchedule.id == schedule_id)
    )
    return result.scalar_one_or_none()
