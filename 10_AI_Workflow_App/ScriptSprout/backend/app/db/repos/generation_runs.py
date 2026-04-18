from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import GenerationRun, GuardrailsEvent


def insert_generation_run(
    db: Session,
    *,
    user_id: int,
    content_id: int,
    status: str = "story_generated",
) -> GenerationRun:
    """Create a new generation run tied to a content item."""

    row = GenerationRun(
        user_id=user_id,
        content_id=content_id,
        status=status,
        story_attempts_used=0,
        guardrails_attempts_used=0,
        failure_reason=None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_generation_run_after_story_and_guardrails(
    db: Session,
    *,
    run_id: int,
    status: str,
    failure_reason: str | None,
    story_attempts_used: int,
    guardrails_attempts_used: int,
) -> None:
    """Finalize a generation run with story/guardrails attempt counts and outcome."""

    row = db.get(GenerationRun, run_id)
    if row is None:
        return
    row.status = status
    row.failure_reason = failure_reason
    row.story_attempts_used = story_attempts_used
    row.guardrails_attempts_used = guardrails_attempts_used
    db.commit()


def insert_guardrails_event(
    db: Session,
    *,
    run_id: int,
    attempt_index: int,
    passed: bool,
    failure_reason: str | None,
) -> GuardrailsEvent:
    """Record a single guardrails check result for a generation run attempt."""

    row = GuardrailsEvent(
        run_id=run_id,
        attempt_index=attempt_index,
        passed=passed,
        failure_reason=failure_reason,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_generation_run_with_events(
    db: Session,
    *,
    run_id: int,
) -> GenerationRun | None:
    """Retrieve data needed for this operation.

    Args:
        db: Active database session for repository operations.
        run_id: Unique identifier for the target resource.

    Returns:
        Result generated for the caller.

    """

    return db.get(GenerationRun, run_id)

