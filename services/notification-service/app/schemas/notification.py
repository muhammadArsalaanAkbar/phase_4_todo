"""Task: T052 — Notification Pydantic schemas per contracts/notification-service-api.yaml.

NotificationResponse and NotificationListResponse for request/response serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    """Response schema for a single notification."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    task_id: uuid.UUID
    notification_type: str
    channel: str
    status: str
    payload: dict
    created_at: datetime
    sent_at: datetime | None = None
    error_message: str | None = None


class NotificationListResponse(BaseModel):
    """Response schema for listing notifications."""

    notifications: list[NotificationResponse]
    total: int
