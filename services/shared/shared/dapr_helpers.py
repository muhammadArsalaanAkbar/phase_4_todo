"""Task: T004 — Shared Dapr client helpers.

Publish_event wrapper using DaprClient with CloudEvents metadata.
All inter-service communication goes through Dapr sidecars.
"""

from __future__ import annotations

import json
import logging

from dapr.clients import DaprClient
from pydantic import BaseModel

logger = logging.getLogger(__name__)

PUBSUB_NAME = "kafka-pubsub"

# CloudEvents type mapping
CLOUDEVENT_TYPES = {
    "task-created": "com.todoai.task.created",
    "task-updated": "com.todoai.task.updated",
    "task-completed": "com.todoai.task.completed",
    "task-deleted": "com.todoai.task.deleted",
    "reminder-fired": "com.todoai.reminder.fired",
}


async def publish_event(
    topic: str,
    event: BaseModel,
    source: str,
    event_type: str | None = None,
) -> None:
    """Publish an event to a Kafka topic via Dapr Pub/Sub.

    Args:
        topic: Kafka topic name (task-events, task-updates, reminders).
        event: Pydantic model to serialize as event data.
        source: Source service name for CloudEvents metadata.
        event_type: Event type key for CloudEvents (e.g., 'task-created').
    """
    data = event.model_dump(mode="json")
    ce_type = CLOUDEVENT_TYPES.get(event_type or "", "com.todoai.event.unknown")

    try:
        with DaprClient() as client:
            client.publish_event(
                pubsub_name=PUBSUB_NAME,
                topic_name=topic,
                data=json.dumps(data),
                data_content_type="application/json",
                metadata={
                    "cloudevent.type": ce_type,
                    "cloudevent.source": source,
                },
            )
        logger.info(
            "Published event to %s: type=%s task_id=%s",
            topic,
            event_type,
            data.get("task_id"),
        )
    except Exception:
        logger.exception("Failed to publish event to %s", topic)
        raise
