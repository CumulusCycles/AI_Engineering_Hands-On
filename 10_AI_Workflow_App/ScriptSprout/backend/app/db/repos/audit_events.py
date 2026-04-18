from __future__ import annotations

import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import AuditEvent


def insert_audit_event(
    db: Session,
    *,
    user_id: int,
    event_type: str,
    entity_type: str,
    entity_id: int,
    payload: dict | None = None,
) -> AuditEvent:
    """Insert a record into persistent storage.

    Args:
        db: Active database session for repository operations.
        user_id: Unique identifier for the target resource.
        event_type: Input value used to perform this operation.
        entity_type: Input value used to perform this operation.
        entity_id: Unique identifier for the target resource.
        payload: Input value used to perform this operation.

    Returns:
        Result generated for the caller.

    """

    row = AuditEvent(
        user_id=user_id,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        payload_json=json.dumps(payload) if payload is not None else None,
    )
    db.add(row)
    db.flush()
    db.refresh(row)
    return row


def count_audit_events(
    db: Session,
    *,
    user_id: int | None = None,
    event_type: str | None = None,
) -> int:
    """Count matching records for reporting or pagination.

    Args:
        db: Active database session for repository operations.
        user_id: Unique identifier for the target resource.
        event_type: Input value used to perform this operation.

    Returns:
        Result generated for the caller.

    """

    stmt = select(func.count()).select_from(AuditEvent)
    if user_id is not None:
        stmt = stmt.where(AuditEvent.user_id == user_id)
    if event_type is not None:
        stmt = stmt.where(AuditEvent.event_type == event_type)
    return int(db.scalar(stmt) or 0)

