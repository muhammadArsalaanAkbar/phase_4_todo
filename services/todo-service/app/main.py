"""Task: T013, T035 — Todo Service FastAPI application.

FastAPI + DaprApp setup with shared health router, tasks router,
structured logging, and DB lifespan management.
Port 8001 per plan.md port assignments.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from shared.health import router as health_router
from shared.logging import setup_logging

from app.config import settings
from app.db.session import engine
from app.routers.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    logger.info("Todo Service starting on port %s", settings.PORT)
    yield
    logger.info("Todo Service shutting down — disposing DB engine")
    await engine.dispose()


logger = setup_logging(settings.SERVICE_NAME, settings.LOG_LEVEL)

app = FastAPI(
    title="Todo Service",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(tasks_router)
