"""Task: T014 — Todo Service configuration.

Service-specific settings: PORT=8001, SERVICE_NAME=todo-service,
DB schema=todo_service.
"""

from __future__ import annotations

from shared.config import BaseServiceConfig


class TodoServiceConfig(BaseServiceConfig):
    """Todo Service specific configuration."""

    SERVICE_NAME: str = "todo-service"
    PORT: int = 8001
    DB_SCHEMA: str = "todo_service"


settings = TodoServiceConfig()
