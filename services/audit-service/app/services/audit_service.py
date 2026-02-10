"""Task: T041 — AuditService business logic.

store_event (idempotent via event_id UNIQUE), list_records (filter by
task_id, event_type), get_record.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_record import AuditRecord

logger = logging.getLogger(__name__)


async def store_event(
    session: AsyncSession,
    event_id: uuid.UUID,
    event_type: str,
    task_id: uuid.UUID,
    payload: dict,
    source_service: str,
) -> AuditRecord | None:
    """Store an audit record. Idempotent — duplicates by event_id are ignored.

    Returns the AuditRecord on success, None if duplicate.
    """
    record = AuditRecord(
        event_id=event_id,
        event_type=event_type,
        task_id=task_id,
        payload=payload,
        source_service=source_service,
    )
    session.add(record)
    try:
        await session.commit()
        await session.refresh(record)
        logger.info(
            "Audit record stored: event_id=%s type=%s task_id=%s",
            event_id,
            event_type,
            task_id,
        )
        return record
    except IntegrityError:
        await session.rollback()
        logger.info(
            "Duplicate event ignored: event_id=%s",
            event_id,
        )
        return None


async def list_records(
    session: AsyncSession,
    task_id: uuid.UUID | None = None,
    event_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[AuditRecord], int]:
    """List audit records with optional filters and pagination."""
    query = select(AuditRecord)
    count_query = select(func.count()).select_from(AuditRecord)

    if task_id:
        query = query.where(AuditRecord.task_id == task_id)
        count_query = count_query.where(AuditRecord.task_id == task_id)

    if event_type:
        query = query.where(AuditRecord.event_type == event_type)
        count_query = count_query.where(AuditRecord.event_type == event_type)

    query = query.order_by(AuditRecord.recorded_at.desc()).limit(limit).offset(offset)

    result = await session.execute(query)
    records = list(result.scalars().all())

    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    return records, total


async def get_record(
    session: AsyncSession, record_id: uuid.UUID
) -> AuditRecord | None:
    """Get a single audit record by ID."""
    result = await session.execute(
        select(AuditRecord).where(AuditRecord.id == record_id)
    )
    return result.scalar_one_or_none()
