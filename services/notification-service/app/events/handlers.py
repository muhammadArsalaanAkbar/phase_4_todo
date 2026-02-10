"""Task: T054 — Dapr Pub/Sub event handler for Notification Service.

Subscribes to reminders topic on kafka-pubsub. Parses ReminderEvent,
calls NotificationService.create_notification + deliver_notification.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import Request

from app.db.session import async_session_factory
from app.services import notification_service

logger = logging.getLogger(__name__)

PUBSUB_NAME = "kafka-pubsub"
TOPIC_NAME = "reminders"


async def handle_reminder_event(request: Request) -> dict:
    """Handle incoming reminder event from Dapr Pub/Sub.

    Creates a notification record and immediately attempts delivery.
    """
    body = await request.json()
    logger.info("Received reminder event: %s", body.get("type", "unknown"))

    # Dapr CloudEvents: data contains our ReminderEvent payload
    data = body.get("data", body)

    task_id = uuid.UUID(str(data["task_id"]))
    payload_data = data.get("payload", {})

    # Build notification payload from reminder event
    notification_payload = {
        "title": payload_data.get("title", "Task reminder"),
        "reminder_time": payload_data.get("reminder_time", ""),
        "event_id": str(data.get("event_id", "")),
    }

    async with async_session_factory() as session:
        # Create the notification record
        notification = await notification_service.create_notification(
            session=session,
            task_id=task_id,
            notification_type="reminder",
            payload=notification_payload,
            channel=payload_data.get("channel", "in_app"),
        )

        # Attempt immediate delivery
        try:
            await notification_service.deliver_notification(session, notification)
            logger.info("Notification delivered: %s", notification.id)
        except Exception as exc:
            await notification_service.handle_failure(
                session, notification, str(exc)
            )
            logger.error(
                "Notification delivery failed: %s error=%s",
                notification.id,
                exc,
            )

    return {"status": "SUCCESS"}
