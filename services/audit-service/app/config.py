"""Task: T019 — Audit Service configuration.

Service-specific settings: PORT=8002, SERVICE_NAME=audit-service,
DB schema=audit_service.
"""

from __future__ import annotations

from shared.config import BaseServiceConfig


class AuditServiceConfig(BaseServiceConfig):
    """Audit Service specific configuration."""

    SERVICE_NAME: str = "audit-service"
    PORT: int = 8002
    DB_SCHEMA: str = "audit_service"


settings = AuditServiceConfig()
