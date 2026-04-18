from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.db.models import AuditEvent, ContentItem, GenerationRun, GuardrailsEvent, ModelCall
from app.schemas.admin_metrics import (
    AdminMetricsResponse,
    AuditEventMetricsBlock,
    ContentMetricsBlock,
    GenerationRunMetricsBlock,
    GuardrailsEventMetricsBlock,
    LabelCountBucket,
    MetricsTimeWindow,
    ModelCallMetricsBlock,
)

DEFAULT_METRICS_WINDOW = timedelta(days=7)
MAX_METRICS_SPAN = timedelta(days=366)


def ensure_utc(dt: datetime) -> datetime:
    """Normalize a datetime to timezone-aware UTC.

    Args:
        dt: Datetime value received from query parsing or internal logic.

    Returns:
        UTC-aware datetime value.
    """
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def resolve_metrics_window(
    start: datetime | None,
    end: datetime | None,
) -> tuple[datetime, datetime, bool]:
    """Resolve and validate the admin metrics time window.

    Args:
        start: Optional inclusive range start from the query string.
        end: Optional inclusive range end from the query string.

    Returns:
        Tuple of ``(start_utc, end_utc, used_default_window)``.

    Raises:
        ValueError: If the window bounds are invalid or exceed the max span.
    """
    now = datetime.now(tz=UTC)
    used_default = start is None and end is None
    start_u = ensure_utc(start) if start is not None else None
    end_u = ensure_utc(end) if end is not None else None

    if end_u is None:
        end_u = now
    if start_u is None:
        start_u = end_u - DEFAULT_METRICS_WINDOW

    if start_u > end_u:
        raise ValueError("start must be on or before end")
    if end_u - start_u > MAX_METRICS_SPAN:
        raise ValueError(f"time range must not exceed {MAX_METRICS_SPAN.days} days")

    return start_u, end_u, used_default


def _created_between(col, start: datetime, end: datetime):
    """Build an inclusive ``created_at`` predicate for SQLAlchemy queries.

    Args:
        col: SQLAlchemy datetime column expression.
        start: Inclusive range start.
        end: Inclusive range end.
    """
    return and_(col >= start, col <= end)


def _sorted_buckets(rows: list[tuple[str, int]]) -> list[LabelCountBucket]:
    """Convert grouped rows into sorted label/count buckets.

    Args:
        rows: Aggregated rows from SQL queries in ``(label, count)`` shape.

    Returns:
        Deterministically sorted buckets by descending count then label.
    """
    buckets = [LabelCountBucket(label=label, count=int(n)) for label, n in rows]
    buckets.sort(key=lambda b: (-b.count, b.label))
    return buckets


def compute_admin_metrics(
    db: Session,
    start: datetime,
    end: datetime,
    *,
    used_default_window: bool,
) -> AdminMetricsResponse:
    """Compute admin dashboard metrics for a single UTC window.

    Args:
        db: Active database session for read-only aggregation queries.
        start: Inclusive range start.
        end: Inclusive range end.
        used_default_window: Whether the caller omitted both bounds.

    Returns:
        Fully populated metrics response for dashboard and API consumers.
    """
    content_total = int(
        db.scalar(
            select(func.count(ContentItem.id)).where(
                _created_between(ContentItem.created_at, start, end)
            )
        )
        or 0
    )
    content_by_status_rows = list(
        db.execute(
            select(ContentItem.status, func.count(ContentItem.id))
            .where(_created_between(ContentItem.created_at, start, end))
            .group_by(ContentItem.status)
        )
    )
    content_by_genre_rows = list(
        db.execute(
            select(func.coalesce(ContentItem.genre, "(none)"), func.count(ContentItem.id))
            .where(_created_between(ContentItem.created_at, start, end))
            .group_by(func.coalesce(ContentItem.genre, "(none)"))
        )
    )

    model_total = int(
        db.scalar(
            select(func.count(ModelCall.id)).where(
                _created_between(ModelCall.created_at, start, end)
            )
        )
        or 0
    )
    model_success = int(
        db.scalar(
            select(func.count(ModelCall.id)).where(
                _created_between(ModelCall.created_at, start, end),
                ModelCall.success.is_(True),
            )
        )
        or 0
    )
    model_failure = int(
        db.scalar(
            select(func.count(ModelCall.id)).where(
                _created_between(ModelCall.created_at, start, end),
                ModelCall.success.is_(False),
            )
        )
        or 0
    )
    model_avg_latency = db.scalar(
        select(func.avg(ModelCall.latency_ms)).where(
            _created_between(ModelCall.created_at, start, end)
        )
    )
    model_token_input = db.scalar(
        select(func.sum(ModelCall.token_input)).where(
            _created_between(ModelCall.created_at, start, end)
        )
    )
    model_token_output = db.scalar(
        select(func.sum(ModelCall.token_output)).where(
            _created_between(ModelCall.created_at, start, end)
        )
    )
    model_by_purpose_rows = list(
        db.execute(
            select(func.coalesce(ModelCall.purpose, "(none)"), func.count(ModelCall.id))
            .where(_created_between(ModelCall.created_at, start, end))
            .group_by(func.coalesce(ModelCall.purpose, "(none)"))
        )
    )
    model_by_model_rows = list(
        db.execute(
            select(func.coalesce(ModelCall.model_name, "(none)"), func.count(ModelCall.id))
            .where(_created_between(ModelCall.created_at, start, end))
            .group_by(func.coalesce(ModelCall.model_name, "(none)"))
        )
    )

    runs_total = int(
        db.scalar(
            select(func.count(GenerationRun.id)).where(
                _created_between(GenerationRun.created_at, start, end)
            )
        )
        or 0
    )
    runs_by_status_rows = list(
        db.execute(
            select(GenerationRun.status, func.count(GenerationRun.id))
            .where(_created_between(GenerationRun.created_at, start, end))
            .group_by(GenerationRun.status)
        )
    )
    runs_avg_story_attempts = db.scalar(
        select(func.avg(GenerationRun.story_attempts_used)).where(
            _created_between(GenerationRun.created_at, start, end)
        )
    )
    runs_avg_guardrails_attempts = db.scalar(
        select(func.avg(GenerationRun.guardrails_attempts_used)).where(
            _created_between(GenerationRun.created_at, start, end)
        )
    )

    guardrails_total = int(
        db.scalar(
            select(func.count(GuardrailsEvent.id)).where(
                _created_between(GuardrailsEvent.created_at, start, end)
            )
        )
        or 0
    )
    guardrails_passed = int(
        db.scalar(
            select(func.count(GuardrailsEvent.id)).where(
                _created_between(GuardrailsEvent.created_at, start, end),
                GuardrailsEvent.passed.is_(True),
            )
        )
        or 0
    )
    guardrails_failed = int(
        db.scalar(
            select(func.count(GuardrailsEvent.id)).where(
                _created_between(GuardrailsEvent.created_at, start, end),
                GuardrailsEvent.passed.is_(False),
            )
        )
        or 0
    )

    audit_total = int(
        db.scalar(
            select(func.count(AuditEvent.id)).where(
                _created_between(AuditEvent.created_at, start, end)
            )
        )
        or 0
    )
    audit_by_type_rows = list(
        db.execute(
            select(AuditEvent.event_type, func.count(AuditEvent.id))
            .where(_created_between(AuditEvent.created_at, start, end))
            .group_by(AuditEvent.event_type)
        )
    )

    return AdminMetricsResponse(
        window=MetricsTimeWindow(start=start, end=end, used_default_window=used_default_window),
        content=ContentMetricsBlock(
            items_created=content_total,
            by_status=_sorted_buckets(content_by_status_rows),
            by_genre=_sorted_buckets(content_by_genre_rows),
        ),
        model_calls=ModelCallMetricsBlock(
            total=model_total,
            success_count=model_success,
            failure_count=model_failure,
            avg_latency_ms=float(model_avg_latency) if model_avg_latency is not None else None,
            total_token_input=int(model_token_input) if model_token_input is not None else None,
            total_token_output=int(model_token_output) if model_token_output is not None else None,
            by_purpose=_sorted_buckets(model_by_purpose_rows),
            by_model=_sorted_buckets(model_by_model_rows),
        ),
        generation_runs=GenerationRunMetricsBlock(
            total=runs_total,
            by_status=_sorted_buckets(runs_by_status_rows),
            avg_story_attempts=(
                float(runs_avg_story_attempts) if runs_avg_story_attempts is not None else None
            ),
            avg_guardrails_attempts=(
                float(runs_avg_guardrails_attempts)
                if runs_avg_guardrails_attempts is not None
                else None
            ),
        ),
        guardrails=GuardrailsEventMetricsBlock(
            events_total=guardrails_total,
            passed_count=guardrails_passed,
            failed_count=guardrails_failed,
        ),
        audit=AuditEventMetricsBlock(
            events_total=audit_total,
            by_event_type=_sorted_buckets(audit_by_type_rows),
        ),
    )
