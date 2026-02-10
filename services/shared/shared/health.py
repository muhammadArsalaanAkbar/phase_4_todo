"""Task: T007 — Shared health check router per FR-013.

Provides /health (liveness) and /health/ready (readiness) endpoints
that all microservices include in their FastAPI app.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def liveness() -> dict:
    """Liveness probe — returns 200 if the process is running."""
    return {"status": "healthy"}


@router.get("/health/ready")
async def readiness() -> dict:
    """Readiness probe — returns 200 if the service is ready to accept traffic."""
    return {"status": "ready"}
