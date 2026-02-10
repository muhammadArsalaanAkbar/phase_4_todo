"""Task: T044 — Audit Service main application (updated from T018).

FastAPI + DaprApp setup with health router, audit query router,
and Dapr Pub/Sub event handler for task-events topic.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from shared.health import router as health_router
from shared.logging import setup_logging

from app.config import settings
from app.db.session import engine
from app.events.handlers import PUBSUB_NAME, TOPIC_NAME, handle_task_event
from app.routers.audit import router as audit_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    logger.info("Audit Service starting on port %s", settings.PORT)
    yield
    logger.info("Audit Service shutting down — disposing DB engine")
    await engine.dispose()


logger = setup_logging(settings.SERVICE_NAME, settings.LOG_LEVEL)

app = FastAPI(
    title="Audit Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(audit_router)


# Dapr Pub/Sub subscription endpoint — Dapr calls this to discover subscriptions
@app.get("/dapr/subscribe")
async def subscribe():
    """Return Dapr subscription configuration."""
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_NAME,
            "route": "/events/task-events",
        }
    ]


# Dapr delivers events to this endpoint
@app.post("/events/task-events")
async def task_events_handler(request: Request):
    """Handle task events from Dapr Pub/Sub."""
    return await handle_task_event(request)
