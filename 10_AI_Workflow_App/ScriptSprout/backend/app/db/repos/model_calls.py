from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import ModelCall


def insert_model_call(
    db: Session,
    *,
    user_id: int,
    operation_type: str,
    model_name: str,
    purpose: str,
    attempt_index: int,
    success: bool,
    latency_ms: int,
    token_input: int | None = None,
    token_output: int | None = None,
    error_type: str | None = None,
    run_id: int | None = None,
) -> ModelCall:
    """Record a single LLM/model API call with its latency and token usage."""

    row = ModelCall(
        run_id=run_id,
        user_id=user_id,
        operation_type=operation_type,
        model_name=model_name,
        purpose=purpose,
        attempt_index=attempt_index,
        success=success,
        latency_ms=latency_ms,
        token_input=token_input,
        token_output=token_output,
        error_type=error_type,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def count_model_calls(db: Session) -> int:
    """Return the total number of model call records."""

    return int(db.scalar(select(func.count()).select_from(ModelCall)) or 0)


def list_model_calls(
    db: Session,
    *,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[ModelCall], int]:
    """Return paginated model calls (newest first) and the total count."""

    total = int(db.scalar(select(func.count()).select_from(ModelCall)) or 0)
    stmt = select(ModelCall).order_by(ModelCall.id.desc()).limit(limit).offset(offset)
    rows = list(db.scalars(stmt).all())
    return rows, total
