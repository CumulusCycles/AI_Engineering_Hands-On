"""Request/response models for admin NLP orchestration."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.admin_metrics import AdminMetricsResponse
from app.schemas.search import SemanticSearchResponse


class AdminNlpQueryRequest(BaseModel):
    """Natural-language question from an admin operator."""

    query: str = Field(
        min_length=1,
        max_length=16_000,
        description="Admin question; routed to metrics and/or semantic search tools.",
    )


class AdminQueryPlanParsed(BaseModel):
    """Structured routing plan from ``responses.parse`` (not returned verbatim to clients)."""

    run_metrics: bool = Field(
        description="True when SQLite metrics aggregates help answer the question.",
    )
    run_semantic_search: bool = Field(
        description="True when vector search over indexed story text helps.",
    )
    metrics_start_iso: str | None = Field(
        default=None,
        description="Inclusive metrics window start (ISO 8601 UTC). Null to pair with defaults.",
    )
    metrics_end_iso: str | None = Field(
        default=None,
        description=(
            "Inclusive metrics window end (ISO 8601 UTC). Null defaults to now when needed."
        ),
    )
    semantic_query: str | None = Field(
        default=None,
        description="Text to embed for Chroma; null means reuse the admin question.",
    )
    semantic_limit: int = Field(default=10, ge=1, le=50)
    semantic_genre: str | None = Field(default=None, max_length=128)
    semantic_status: str | None = Field(default=None, max_length=64)
    brief_summary: str = Field(
        description="One short sentence: how the question was interpreted.",
    )


class AdminNlpQueryResponse(BaseModel):
    """Composed tool outputs plus parse metadata."""

    query: str = Field(description="Echo of the request ``query``.")
    plan_summary: str = Field(description="Model-generated interpretation (``brief_summary``).")
    metrics: AdminMetricsResponse | None = Field(
        default=None,
        description="Present when the plan enabled the metrics tool.",
    )
    semantic_search: SemanticSearchResponse | None = Field(
        default=None,
        description="Present when the plan enabled semantic search (may be empty items).",
    )
    parse_attempts_used: int = Field(
        ge=1,
        description="OpenAI ``responses.parse`` attempts for the routing step.",
    )
