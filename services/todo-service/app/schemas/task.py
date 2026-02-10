"""Task: T032 — Task Pydantic schemas per contracts/todo-service-api.yaml.

TaskCreate, TaskUpdate, TaskResponse, TaskListResponse for request/response
validation and serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """Allowed task status values."""

    pending = "pending"
    in_progress = "in_progress"
    complete = "complete"


class RecurrenceSchedule(str, Enum):
    """Allowed recurrence schedule values."""

    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class TaskCreate(BaseModel):
    """Request schema for creating a task."""

    title: str = Field(..., max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    reminder_time: datetime | None = None
    is_recurring: bool = False
    recurrence_schedule: RecurrenceSchedule | None = None


class TaskUpdate(BaseModel):
    """Request schema for updating a task. All fields optional."""

    title: str | None = Field(None, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    due_date: datetime | None = None
    reminder_time: datetime | None = None
    is_recurring: bool | None = None
    recurrence_schedule: RecurrenceSchedule | None = None


class TaskResponse(BaseModel):
    """Response schema for a single task."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str | None = None
    status: str
    due_date: datetime | None = None
    reminder_time: datetime | None = None
    is_recurring: bool
    recurrence_schedule: str | None = None
    created_at: datetime
    updated_at: datetime


class TaskListResponse(BaseModel):
    """Response schema for listing tasks."""

    tasks: list[TaskResponse]
    total: int
