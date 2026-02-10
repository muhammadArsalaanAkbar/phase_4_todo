"""Task: T048 — WebSocket Service main application (updated from T020).

FastAPI with WebSocket endpoint /ws, connection count endpoint
/api/v1/connections, health router, and Dapr Pub/Sub subscription
for task-updates topic.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect

from shared.health import router as health_router
from shared.logging import setup_logging

from app.config import settings
from app.events.handlers import PUBSUB_NAME, TOPIC_NAME, handle_task_update
from app.ws.manager import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    logger.info("WebSocket Service starting on port %s", settings.PORT)
    yield
    logger.info("WebSocket Service shutting down")


logger = setup_logging(settings.SERVICE_NAME, settings.LOG_LEVEL)

app = FastAPI(
    title="WebSocket Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection endpoint for real-time task updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive — wait for client messages (or disconnect)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/v1/connections")
async def get_connection_count():
    """Get active WebSocket connection count."""
    return {"active_connections": manager.active_count}


# Dapr Pub/Sub subscription endpoint
@app.get("/dapr/subscribe")
async def subscribe():
    """Return Dapr subscription configuration."""
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_NAME,
            "route": "/events/task-updates",
        }
    ]


# Dapr delivers events to this endpoint
@app.post("/events/task-updates")
async def task_updates_handler(request: Request):
    """Handle task update events from Dapr Pub/Sub."""
    return await handle_task_update(request)
