"""Task: T047 — Dapr Pub/Sub event handler for WebSocket Service.

Subscribes to task-updates topic on kafka-pubsub. Parses TaskEvent
and calls ConnectionManager.broadcast to push to all connected clients.
"""

from __future__ import annotations

import logging

from fastapi import Request

from app.ws.manager import manager

logger = logging.getLogger(__name__)

PUBSUB_NAME = "kafka-pubsub"
TOPIC_NAME = "task-updates"


async def handle_task_update(request: Request) -> dict:
    """Handle incoming task update event from Dapr Pub/Sub.

    Broadcasts the event payload to all connected WebSocket clients.
    """
    body = await request.json()
    logger.info("Received task update event: %s", body.get("type", "unknown"))

    # Dapr CloudEvents: data contains our TaskEvent payload
    data = body.get("data", body)

    message = {
        "event_type": data.get("event_type", "unknown"),
        "task_id": str(data.get("task_id", "")),
        "timestamp": data.get("timestamp", ""),
        "payload": data.get("payload", {}),
    }

    await manager.broadcast(message)

    return {"status": "SUCCESS"}
