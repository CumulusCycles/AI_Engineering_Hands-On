from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models import GenerationRun


class GuardrailsEventItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    attempt_index: int
    passed: bool
    failure_reason: str | None
    created_at: datetime


class AdminGenerationRunDetail(BaseModel):
    """Admin-only read model for one generation run."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    content_id: int
    status: str
    failure_reason: str | None
    story_attempts_used: int
    guardrails_attempts_used: int
    created_at: datetime
    updated_at: datetime

    events: list[GuardrailsEventItem]


def generation_run_to_admin_detail(row: GenerationRun) -> AdminGenerationRunDetail:
    """Convert a GenerationRun DB row (with events) to an admin detail schema."""

    events_sorted = sorted(
        getattr(row, "events", []) or [],
        key=lambda e: e.attempt_index,
    )
    return AdminGenerationRunDetail(
        id=row.id,
        content_id=row.content_id,
        status=row.status,
        failure_reason=row.failure_reason,
        story_attempts_used=row.story_attempts_used,
        guardrails_attempts_used=row.guardrails_attempts_used,
        created_at=row.created_at,
        updated_at=getattr(row, "updated_at", row.created_at),
        events=[GuardrailsEventItem.model_validate(e) for e in events_sorted],
    )

