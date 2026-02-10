"""Task: T065 — Recurring Task Service main application (updated from T024).

FastAPI with APScheduler lifespan integration, health router, schedules
query router, and Dapr Pub/Sub subscription for task-events topic.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from shared.health import router as health_router
from shared.logging import setup_logging

from app.config import settings
from app.db.session import engine
from app.events.handlers import PUBSUB_NAME, TOPIC_NAME, handle_task_event
from app.routers.schedules import router as schedules_router
from app.scheduler.jobs import shutdown_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    logger.info("Recurring Task Service starting on port %s", settings.PORT)
    start_scheduler()
    yield
    logger.info("Recurring Task Service shutting down")
    shutdown_scheduler()
    await engine.dispose()


logger = setup_logging(settings.SERVICE_NAME, settings.LOG_LEVEL)

app = FastAPI(
    title="Recurring Task Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(schedules_router)


# Dapr Pub/Sub subscription endpoint
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
