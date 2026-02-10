"""Task: T064 — Schedules query router per contracts/recurring-task-service-api.yaml.

REST endpoints:
  GET /api/v1/schedules                — List recurrence schedules (filter: is_active)
  GET /api/v1/schedules/{schedule_id}  — Get specific schedule
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.recurrence import RecurrenceListResponse, RecurrenceResponse
from app.services import recurrence_service

router = APIRouter(prefix="/api/v1/schedules", tags=["schedules"])


@router.get("", response_model=RecurrenceListResponse)
async def list_schedules(
    is_active: bool | None = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> RecurrenceListResponse:
    """List recurrence schedules with optional is_active filter."""
    schedules, total = await recurrence_service.list_schedules(
        session, is_active=is_active, limit=limit, offset=offset
    )
    return RecurrenceListResponse(
        schedules=[RecurrenceResponse.model_validate(s) for s in schedules],
        total=total,
    )


@router.get("/{schedule_id}", response_model=RecurrenceResponse)
async def get_schedule(
    schedule_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> RecurrenceResponse:
    """Get a specific recurrence schedule by ID."""
    schedule = await recurrence_service.get_schedule(session, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return RecurrenceResponse.model_validate(schedule)
