"""Task: T042 — Dapr Pub/Sub event handler for Audit Service.

Subscribes to task-events topic on kafka-pubsub. Parses TaskEvent
and calls AuditService.store_event with idempotency via event_id UNIQUE.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import Request

from app.db.session import async_session_factory
from app.services import audit_service

logger = logging.getLogger(__name__)

PUBSUB_NAME = "kafka-pubsub"
TOPIC_NAME = "task-events"


async def handle_task_event(request: Request) -> dict:
    """Handle incoming task event from Dapr Pub/Sub.

    Dapr delivers CloudEvents — the event data is in the request body.
    """
    body = await request.json()
    logger.info("Received task event: %s", body.get("type", "unknown"))

    # Dapr CloudEvents: data contains our TaskEvent payload
    data = body.get("data", body)

    event_id = uuid.UUID(str(data["event_id"]))
    event_type = data["event_type"]
    task_id = uuid.UUID(str(data["task_id"]))
    payload = data.get("payload", {})
    source_service = body.get("source", data.get("source_service", "unknown"))

    async with async_session_factory() as session:
        record = await audit_service.store_event(
            session=session,
            event_id=event_id,
            event_type=event_type,
            task_id=task_id,
            payload=payload,
            source_service=source_service,
        )

    if record:
        logger.info("Audit record created: %s", record.id)
    else:
        logger.info("Duplicate event skipped: event_id=%s", event_id)

    return {"status": "SUCCESS"}
