"""Task: T040 — AuditRecord Pydantic schemas per contracts/audit-service-api.yaml.

AuditRecordResponse and AuditListResponse for request/response serialization.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuditRecordResponse(BaseModel):
    """Response schema for a single audit record."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_id: uuid.UUID
    event_type: str
    task_id: uuid.UUID
    payload: dict
    source_service: str
    recorded_at: datetime


class AuditListResponse(BaseModel):
    """Response schema for listing audit records."""

    records: list[AuditRecordResponse]
    total: int
