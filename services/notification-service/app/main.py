"""Task: T056 — Notification Service main application (updated from T022).

FastAPI with health router, notifications query router, and Dapr Pub/Sub
subscription for reminders topic. DB engine disposal in lifespan.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from shared.health import router as health_router
from shared.logging import setup_logging

from app.config import settings
from app.db.session import engine
from app.events.handlers import PUBSUB_NAME, TOPIC_NAME, handle_reminder_event
from app.routers.notifications import router as notifications_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    logger.info("Notification Service starting on port %s", settings.PORT)
    yield
    logger.info("Notification Service shutting down — disposing DB engine")
    await engine.dispose()


logger = setup_logging(settings.SERVICE_NAME, settings.LOG_LEVEL)

app = FastAPI(
    title="Notification Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(notifications_router)


# Dapr Pub/Sub subscription endpoint
@app.get("/dapr/subscribe")
async def subscribe():
    """Return Dapr subscription configuration."""
    return [
        {
            "pubsubname": PUBSUB_NAME,
            "topic": TOPIC_NAME,
            "route": "/events/reminders",
        }
    ]


# Dapr delivers events to this endpoint
@app.post("/events/reminders")
async def reminders_handler(request: Request):
    """Handle reminder events from Dapr Pub/Sub."""
    return await handle_reminder_event(request)
