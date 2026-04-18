"""Synopsis generation via OpenAI Responses API."""

from __future__ import annotations

from typing import Any

from openai import OpenAI
from sqlalchemy.orm import Session

from app.db.models import ContentItem
from app.db.repos.model_calls import insert_model_call
from app.schemas.synopsis import GenerateSynopsisResponse
from app.services.openai_helpers import usage_tokens as _usage_tokens
from app.services.openai_retry import call_with_transient_retry

_MAX_OUTPUT_CHARS = 4_000


def _build_synopsis_prompt(content: ContentItem) -> str:
    """Assemble the prompt that asks OpenAI for a concise story synopsis."""

    subject = content.subject or ""
    genre = content.genre or ""
    age_group = content.age_group or ""
    runtime = (
        f"{content.video_length_minutes} minute(s)"
        if content.video_length_minutes is not None
        else ""
    )

    # Keep prompt small and deterministic enough for a tutorial demo.
    return (
        "You write a concise synopsis for a YouTube story video.\n\n"
        f"User request: {content.source_prompt}\n"
        + (f"Subject/premise: {subject}\n" if subject else "")
        + (f"Genre: {genre}\n" if genre else "")
        + (f"Audience: {age_group}\n" if age_group else "")
        + (f"Target length: {runtime}\n" if runtime else "")
        + "\n"
        "Write 3–5 sentences capturing the main premise, tone, and hook.\n"
        "Return ONLY the synopsis text (no headings, no bullet points)."
    )


def run_generate_synopsis(
    *,
    client: OpenAI,
    model: str,
    content: ContentItem,
    max_attempts: int = 2,
    db: Session | None = None,
    user_id: int | None = None,
) -> GenerateSynopsisResponse:
    """Generate a synopsis for the given content item via OpenAI."""

    def _create():
        """Call OpenAI to generate a synopsis from the content prompt."""

        return client.responses.create(
            model=model,
            input=_build_synopsis_prompt(content),
        )

    def _after_attempt(
        attempt: int,
        latency_ms: float,
        exc: BaseException | None,
        result: Any | None,
    ) -> None:
        """Log the synopsis-generation model call to the database."""

        if db is None or user_id is None:
            return
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
            user_id=user_id,
            operation_type="responses_create",
            model_name=str(resolved_model),
            purpose="synopsis",
            attempt_index=attempt,
            success=ok,
            latency_ms=max(0, int(round(latency_ms))),
            token_input=ti,
            token_output=to,
            error_type=err,
        )

    resp, attempts_used = call_with_transient_retry(
        _create,
        max_attempts=max_attempts,
        after_attempt=_after_attempt,
    )

    text = (getattr(resp, "output_text", None) or "").strip()
    if not text:
        # This is treated as an upstream content failure (and should be visible to the author).
        raise RuntimeError("OpenAI returned empty synopsis output")
    if len(text) > _MAX_OUTPUT_CHARS:
        text = text[: _MAX_OUTPUT_CHARS - 1] + "…"

    # Store immediately in the content row.
    content.synopsis = text
    content.status = "synopsis_generated"

    return GenerateSynopsisResponse(
        content_id=content.id,
        synopsis=text,
        status=content.status,
        attempts_used=attempts_used,
        openai_response_id=getattr(resp, "id", None),
    )

