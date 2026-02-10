"""Task: T053 — NotificationService business logic.

create_notification, deliver_notification (in-app channel: mark as sent),
list_notifications (filter by status, task_id), handle_failure
(mark as failed with error_message).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification

logger = logging.getLogger(__name__)


async def create_notification(
    session: AsyncSession,
    task_id: uuid.UUID,
    notification_type: str,
    payload: dict,
    channel: str = "in_app",
) -> Notification:
    """Create a new notification record with status=pending."""
    notification = Notification(
        task_id=task_id,
        notification_type=notification_type,
        channel=channel,
        payload=payload,
    )
    session.add(notification)
    await session.commit()
    await session.refresh(notification)

    logger.info(
        "Notification created: %s type=%s task_id=%s",
        notification.id,
        notification_type,
        task_id,
    )
    return notification


async def deliver_notification(
    session: AsyncSession,
    notification: Notification,
) -> Notification:
    """Deliver a notification via its channel.

    For in_app channel: marks as sent immediately.
    Returns the updated notification.
    """
    if notification.channel == "in_app":
        notification.status = "sent"
        notification.sent_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(notification)

        logger.info(
            "Notification delivered: %s (in_app)",
            notification.id,
        )
    else:
        logger.warning(
            "Unsupported channel: %s for notification %s",
            notification.channel,
            notification.id,
        )

    return notification


async def handle_failure(
    session: AsyncSession,
    notification: Notification,
    error_message: str,
) -> Notification:
    """Mark a notification as failed with an error message."""
    notification.status = "failed"
    notification.error_message = error_message
    await session.commit()
    await session.refresh(notification)

    logger.error(
        "Notification failed: %s error=%s",
        notification.id,
        error_message,
    )
    return notification


async def list_notifications(
    session: AsyncSession,
    status: str | None = None,
    task_id: uuid.UUID | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Notification], int]:
    """List notifications with optional status and task_id filters."""
    query = select(Notification)
    count_query = select(func.count()).select_from(Notification)

    if status:
        query = query.where(Notification.status == status)
        count_query = count_query.where(Notification.status == status)

    if task_id:
        query = query.where(Notification.task_id == task_id)
        count_query = count_query.where(Notification.task_id == task_id)

    query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)

    result = await session.execute(query)
    notifications = list(result.scalars().all())

    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    return notifications, total
