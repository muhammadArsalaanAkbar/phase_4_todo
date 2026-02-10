"""Task: T063 — Dapr Pub/Sub event handler for Recurring Task Service.

Subscribes to task-events topic on kafka-pubsub. Routes by event_type:
  task-created    → handle_task_created
  task-completed  → handle_task_completed
  task-deleted    → handle_task_deleted

Also schedules reminders via APScheduler when reminder_time is present.
"""

from __future__ import annotations

import logging

from fastapi import Request

from app.db.session import async_session_factory
from app.scheduler.jobs import schedule_reminder
from app.services import recurrence_service

logger = logging.getLogger(__name__)

PUBSUB_NAME = "kafka-pubsub"
TOPIC_NAME = "task-events"

# Map event types to handler functions
EVENT_HANDLERS = {
    "task-created": recurrence_service.handle_task_created,
    "task-completed": recurrence_service.handle_task_completed,
    "task-deleted": recurrence_service.handle_task_deleted,
}


async def handle_task_event(request: Request) -> dict:
    """Handle incoming task event from Dapr Pub/Sub.

    Routes to the appropriate handler based on event_type.
    """
    body = await request.json()
    logger.info("Received task event: %s", body.get("type", "unknown"))

    # Dapr CloudEvents: data contains our TaskEvent payload
    data = body.get("data", body)
    event_type = data.get("event_type", "unknown")

    handler = EVENT_HANDLERS.get(event_type)
    if handler:
        async with async_session_factory() as session:
            await handler(session, data)
    else:
        logger.warning("Unhandled event type: %s", event_type)

    # Schedule reminder if task-created has reminder_time
    if event_type == "task-created":
        payload = data.get("payload", {})
        reminder_time = payload.get("reminder_time")
        if reminder_time:
            task_id = str(data.get("task_id", ""))
            title = payload.get("title", "Task reminder")
            schedule_reminder(task_id, title, reminder_time)

    return {"status": "SUCCESS"}
