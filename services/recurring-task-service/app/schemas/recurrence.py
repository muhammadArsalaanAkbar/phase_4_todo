"""Task: T060 — RecurrenceSchedule Pydantic schemas per contracts/recurring-task-service-api.yaml.

RecurrenceResponse and RecurrenceListResponse for request/response serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RecurrenceResponse(BaseModel):
    """Response schema for a single recurrence schedule."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    parent_task_id: uuid.UUID
    frequency: str
    next_due_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RecurrenceListResponse(BaseModel):
    """Response schema for listing recurrence schedules."""

    schedules: list[RecurrenceResponse]
    total: int
