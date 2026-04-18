"""Orchestrate admin NL questions via OpenAI parse + metrics / semantic search tools."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from chromadb.api.models.Collection import Collection
from openai import OpenAI
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import User
from app.db.repos.admin_metrics import (
    compute_admin_metrics,
    ensure_utc,
    resolve_metrics_window,
)
from app.db.repos.model_calls import insert_model_call
from app.schemas.admin_nlp_query import (
    AdminNlpQueryResponse,
    AdminQueryPlanParsed,
)
from app.schemas.search import SemanticSearchHit, SemanticSearchResponse
from app.services.openai_helpers import usage_tokens as _usage_tokens
from app.services.openai_retry import call_with_transient_retry
from app.services.semantic_search import run_semantic_search

logger = logging.getLogger(__name__)


def _parse_metrics_iso(value: str | None) -> datetime | None:
    """Parse an ISO 8601 string into a UTC datetime, returning None on failure."""

    if value is None or not str(value).strip():
        return None
    s = str(value).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        logger.warning("Ignoring unparsable admin NLP metrics window ISO: %r", value)
        return None
    return ensure_utc(dt)


def _build_instructions(now: datetime) -> str:
    """Build the system instructions for the admin NLP query plan parser."""
    now_iso = now.astimezone(UTC).isoformat().replace("+00:00", "Z")
    return (
        "You route an admin's natural-language question to backend analytics tools.\n"
        f"Current UTC time: {now_iso}\n"
        "Tools:\n"
        "- Metrics (SQLite): counts and KPIs for content_items, model_calls, generation_runs, "
        "guardrails_events, audit_events over an inclusive created_at window.\n"
        "- Semantic search: embed text; find similar indexed story text "
        "(title/description/story).\n"
        "Set run_metrics=true for counts, volume, breakdowns by genre/status, failures, usage, "
        "'how many', 'this week', 'today', KPIs, audits.\n"
        "Set run_semantic_search=true for thematic matches, 'stories about …', similarity — "
        "not pure aggregates.\n"
        "Both may be true.\n"
        "For time ranges output metrics_start_iso and metrics_end_iso as ISO 8601 UTC "
        "(suffix Z). For 'this week' use start of the current ISO week: Monday 00:00:00 UTC "
        "through this moment as end. For 'today' use UTC midnight today through now.\n"
        "If run_metrics is true but the window is unclear, set both metrics_*_iso to null "
        "(server default: 7 days ending now).\n"
        "semantic_query: concise embedding text when run_semantic_search; null means reuse the "
        "admin's question text.\n"
        "brief_summary: one sentence explaining your interpretation.\n"
    )


def run_admin_nlp_query(  # noqa: C901
    *,
    client: OpenAI,
    model: str,
    user_query: str,
    settings: Settings,
    db: Session,
    user: User,
    chroma_collection: Collection,
    max_attempts: int,
) -> AdminNlpQueryResponse:
    """Route an admin NL question through OpenAI parse, metrics, or semantic search."""

    now = datetime.now(tz=UTC)
    instructions = _build_instructions(now)

    def _parse_once():
        """Call OpenAI responses.parse to produce an AdminQueryPlanParsed."""
        return client.responses.parse(
            model=model,
            input=user_query.strip(),
            text_format=AdminQueryPlanParsed,
            instructions=instructions,
        )

    def _after_attempt(
        attempt: int,
        latency_ms: float,
        exc: BaseException | None,
        result: Any | None,
    ) -> None:
        """Log a model_call row after each parse attempt."""
        ok = exc is None and result is not None
        ti, to = (None, None)
        err: str | None = None
        if ok and result is not None:
            ti, to = _usage_tokens(result)
        if exc is not None:
            err = type(exc).__name__
        resolved_model = model
        if result is not None:
            resolved_model = getattr(result, "model", None) or model
        insert_model_call(
            db,
            user_id=user.id,
            operation_type="responses_parse",
            model_name=str(resolved_model),
            purpose="admin_nlp_query",
            attempt_index=attempt,
            success=ok,
            latency_ms=max(0, int(round(latency_ms))),
            token_input=ti,
            token_output=to,
            error_type=err,
        )

    parse_resp, parse_attempts = call_with_transient_retry(
        _parse_once,
        max_attempts=max_attempts,
        after_attempt=_after_attempt,
    )
    plan = getattr(parse_resp, "output_parsed", None)
    if not isinstance(plan, AdminQueryPlanParsed):
        msg = "OpenAI parse returned no AdminQueryPlanParsed"
        raise RuntimeError(msg)

    run_metrics = plan.run_metrics
    run_search = plan.run_semantic_search
    if not run_metrics and not run_search:
        run_metrics = True
        summary = f"{plan.brief_summary} (metrics default window applied; no tools were selected)."
    else:
        summary = plan.brief_summary

    metrics_payload = None
    if run_metrics:
        m_start = _parse_metrics_iso(plan.metrics_start_iso)
        m_end = _parse_metrics_iso(plan.metrics_end_iso)
        try:
            start_u, end_u, used_default = resolve_metrics_window(m_start, m_end)
        except ValueError:
            start_u, end_u, used_default = resolve_metrics_window(None, None)
        metrics_payload = compute_admin_metrics(
            db, start_u, end_u, used_default_window=used_default
        )

    search_payload = None
    if run_search:
        q_text = (plan.semantic_query or "").strip() or user_query.strip()
        if int(chroma_collection.count()) == 0:
            search_payload = SemanticSearchResponse(
                items=[],
                embedding_model=settings.openai_embedding_model,
                attempts_used=0,
            )
        else:
            hits, att_used, model_used = run_semantic_search(
                client=client,
                embedding_model=settings.openai_embedding_model,
                collection=chroma_collection,
                query_text=q_text,
                limit=plan.semantic_limit,
                db=db,
                user=user,
                max_attempts=max_attempts,
                genre=plan.semantic_genre,
                status=plan.semantic_status,
            )
            search_payload = SemanticSearchResponse(
                items=[SemanticSearchHit(distance=h.distance, content=h.content) for h in hits],
                embedding_model=model_used,
                attempts_used=att_used,
            )

    return AdminNlpQueryResponse(
        query=user_query.strip(),
        plan_summary=summary,
        metrics=metrics_payload,
        semantic_search=search_payload,
        parse_attempts_used=parse_attempts,
    )
