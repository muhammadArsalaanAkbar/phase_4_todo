"""Task: T003 — Shared event schema definitions (Pydantic models).

Defines TaskEvent and ReminderEvent per data-model.md.
All events are published via Dapr Pub/Sub and wrapped in CloudEvents v1.0.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TaskPayload(BaseModel):
    """Payload within a TaskEvent containing task field snapshot."""

    title: str
    description: str | None = None
    status: str = "pending"
    due_date: datetime | None = None
    reminder_time: datetime | None = None
    is_recurring: bool = False
    recurrence_schedule: str | None = None


class TaskEvent(BaseModel):
    """Event published to task-events and task-updates topics.

    Event types: task-created, task-updated, task-completed, task-deleted
    """

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str
    task_id: uuid.UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    schema_version: str = "1.0"
    payload: TaskPayload


class ReminderPayload(BaseModel):
    """Payload within a ReminderEvent."""

    title: str
    reminder_time: datetime
    channel: str = "in_app"


class ReminderEvent(BaseModel):
    """Event published to reminders topic.

    Event types: reminder-fired
    """

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_type: str = "reminder-fired"
    task_id: uuid.UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    schema_version: str = "1.0"
    payload: ReminderPayload
