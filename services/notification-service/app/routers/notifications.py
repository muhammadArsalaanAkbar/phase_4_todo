"""Task: T055 — Notifications query router per contracts/notification-service-api.yaml.

REST endpoint:
  GET /api/v1/notifications — List notifications (filters: status, task_id)
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.notification import NotificationListResponse, NotificationResponse
from app.services import notification_service

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    status: str | None = Query(None),
    task_id: uuid.UUID | None = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> NotificationListResponse:
    """List notifications with optional status and task_id filters."""
    notifications, total = await notification_service.list_notifications(
        session, status=status, task_id=task_id, limit=limit, offset=offset
    )
    return NotificationListResponse(
        notifications=[
            NotificationResponse.model_validate(n) for n in notifications
        ],
        total=total,
    )
