"""Task: T043 — Audit query router per contracts/audit-service-api.yaml.

REST endpoints:
  GET /api/v1/audit              — List audit records (filters: task_id, event_type)
  GET /api/v1/audit/{record_id}  — Get specific audit record
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.audit_record import AuditListResponse, AuditRecordResponse
from app.services import audit_service

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("", response_model=AuditListResponse)
async def list_audit_records(
    task_id: uuid.UUID | None = Query(None),
    event_type: str | None = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> AuditListResponse:
    """List audit records with optional task_id and event_type filters."""
    records, total = await audit_service.list_records(
        session, task_id=task_id, event_type=event_type, limit=limit, offset=offset
    )
    return AuditListResponse(
        records=[AuditRecordResponse.model_validate(r) for r in records],
        total=total,
    )


@router.get("/{record_id}", response_model=AuditRecordResponse)
async def get_audit_record(
    record_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> AuditRecordResponse:
    """Get a specific audit record by ID."""
    record = await audit_service.get_record(session, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Audit record not found")
    return AuditRecordResponse.model_validate(record)
