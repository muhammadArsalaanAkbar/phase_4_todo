"""Task: T062 — APScheduler reminder jobs.

AsyncIOScheduler setup, schedule_reminder (one-time job at reminder_time),
publish_reminder (publish ReminderEvent to reminders topic via Dapr).
Integrates with service lifespan (start/shutdown).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from shared.dapr_helpers import publish_event
from shared.events import ReminderEvent, ReminderPayload

logger = logging.getLogger(__name__)

SOURCE_SERVICE = "recurring-task-service"

scheduler = AsyncIOScheduler()


async def publish_reminder(
    task_id: str, title: str, reminder_time: str
) -> None:
    """Publish a ReminderEvent to the reminders topic via Dapr."""
    event = ReminderEvent(
        task_id=uuid.UUID(task_id),
        payload=ReminderPayload(
            title=title,
            reminder_time=datetime.fromisoformat(reminder_time.replace("Z", "+00:00")),
            channel="in_app",
        ),
    )

    await publish_event(
        topic="reminders",
        event=event,
        source=SOURCE_SERVICE,
        event_type="reminder-fired",
    )

    logger.info("Reminder published for task %s", task_id)


def schedule_reminder(
    task_id: str,
    title: str,
    reminder_time: str,
) -> str | None:
    """Schedule a one-time reminder job at the specified time.

    Returns the job ID on success, None if the time is in the past.
    """
    run_date = datetime.fromisoformat(reminder_time.replace("Z", "+00:00"))

    job_id = f"reminder-{task_id}"

    # Remove existing job for this task if any
    existing = scheduler.get_job(job_id)
    if existing:
        scheduler.remove_job(job_id)

    job = scheduler.add_job(
        publish_reminder,
        "date",
        run_date=run_date,
        args=[task_id, title, reminder_time],
        id=job_id,
        replace_existing=True,
    )

    logger.info(
        "Reminder scheduled: job_id=%s task_id=%s at %s",
        job.id,
        task_id,
        reminder_time,
    )
    return job.id


def start_scheduler() -> None:
    """Start the APScheduler. Call during app startup."""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")


def shutdown_scheduler() -> None:
    """Shutdown the APScheduler gracefully. Call during app shutdown."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler shut down")
