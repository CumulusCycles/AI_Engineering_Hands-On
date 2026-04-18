from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MetricsTimeWindow(BaseModel):
    """Inclusive UTC window applied to row ``created_at`` timestamps."""

    start: datetime = Field(description="Inclusive range start (UTC).")
    end: datetime = Field(description="Inclusive range end (UTC).")
    used_default_window: bool = Field(
        default=False,
        description=(
            "True when both ``start`` and ``end`` query params were omitted; server used a "
            "default window ending at ``end``."
        ),
    )


class LabelCountBucket(BaseModel):
    """Single breakdown row (status, genre, purpose, etc.)."""

    label: str = Field(
        description="Grouping key (e.g. workflow status or ``(none)`` for null genre)."
    )
    count: int = Field(ge=0)


class ContentMetricsBlock(BaseModel):
    """Aggregates for ``content_items`` created in the window."""

    items_created: int = Field(ge=0, description="Rows with ``created_at`` in the window.")
    by_status: list[LabelCountBucket] = Field(description="Counts grouped by ``status``.")
    by_genre: list[LabelCountBucket] = Field(
        description="Counts grouped by ``genre``; null genre appears as ``(none)``."
    )


class ModelCallMetricsBlock(BaseModel):
    """Aggregates for ``model_calls`` in the window."""

    total: int = Field(ge=0)
    success_count: int = Field(ge=0)
    failure_count: int = Field(ge=0)
    avg_latency_ms: float | None = Field(
        default=None,
        description="Mean ``latency_ms`` across attempts; omitted when ``total`` is 0.",
    )
    total_token_input: int | None = Field(
        default=None,
        description="Sum of ``token_input`` (nulls ignored); omitted when no tokens recorded.",
    )
    total_token_output: int | None = Field(
        default=None,
        description="Sum of ``token_output`` (nulls ignored); omitted when no tokens recorded.",
    )
    by_purpose: list[LabelCountBucket]
    by_model: list[LabelCountBucket]


class GenerationRunMetricsBlock(BaseModel):
    """Aggregates for ``generation_runs`` in the window."""

    total: int = Field(ge=0, description="Runs with ``created_at`` in the window.")
    by_status: list[LabelCountBucket]
    avg_story_attempts: float | None = Field(
        default=None,
        description="Mean ``story_attempts_used``; omitted when ``total`` is 0.",
    )
    avg_guardrails_attempts: float | None = Field(
        default=None,
        description="Mean ``guardrails_attempts_used``; omitted when ``total`` is 0.",
    )


class GuardrailsEventMetricsBlock(BaseModel):
    """Aggregates for ``guardrails_events`` in the window (by ``created_at``)."""

    events_total: int = Field(ge=0)
    passed_count: int = Field(ge=0)
    failed_count: int = Field(ge=0)


class AuditEventMetricsBlock(BaseModel):
    """Aggregates for ``audit_events`` in the window."""

    events_total: int = Field(ge=0)
    by_event_type: list[LabelCountBucket]


class AdminMetricsResponse(BaseModel):
    """Admin dashboard metrics for a single time window."""

    window: MetricsTimeWindow
    content: ContentMetricsBlock
    model_calls: ModelCallMetricsBlock
    generation_runs: GenerationRunMetricsBlock
    guardrails: GuardrailsEventMetricsBlock
    audit: AuditEventMetricsBlock
