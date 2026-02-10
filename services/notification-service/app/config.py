"""Task: T023 — Notification Service configuration.

Service-specific settings: PORT=8004, SERVICE_NAME=notification-service,
DB schema=notification_service.
"""

from __future__ import annotations

from shared.config import BaseServiceConfig


class NotificationServiceConfig(BaseServiceConfig):
    """Notification Service specific configuration."""

    SERVICE_NAME: str = "notification-service"
    PORT: int = 8004
    DB_SCHEMA: str = "notification_service"


settings = NotificationServiceConfig()
