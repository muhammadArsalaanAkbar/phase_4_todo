"""Task: T025 — Recurring Task Service configuration.

Service-specific settings: PORT=8005, SERVICE_NAME=recurring-task-service,
DB schema=recurring_task_service. Includes APScheduler dependency.
"""

from __future__ import annotations

from shared.config import BaseServiceConfig


class RecurringTaskServiceConfig(BaseServiceConfig):
    """Recurring Task Service specific configuration."""

    SERVICE_NAME: str = "recurring-task-service"
    PORT: int = 8005
    DB_SCHEMA: str = "recurring_task_service"


settings = RecurringTaskServiceConfig()
