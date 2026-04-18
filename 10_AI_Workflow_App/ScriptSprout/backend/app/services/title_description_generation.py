"""Title + description generation via OpenAI Responses API."""

from __future__ import annotations

from typing import Any

from openai import OpenAI
from sqlalchemy.orm import Session

from app.db.models import ContentItem
from app.db.repos.model_calls import insert_model_call
from app.schemas.synopsis import GenerateDescriptionResponse, GenerateTitleResponse
from app.services.openai_helpers import usage_tokens as _usage_tokens
from app.services.openai_retry import call_with_transient_retry

_MAX_OUTPUT_CHARS = 4_000


def _build_title_prompt(content: ContentItem) -> str:
    """Assemble the prompt that asks OpenAI for a short YouTube title."""

    subject = content.subject or ""
    genre = content.genre or ""
    age_group = content.age_group or ""
    runtime = (
        f"{content.video_length_minutes} minute(s)"
        if content.video_length_minutes is not None
        else ""
    )
    synopsis = (content.synopsis or "").strip()

    # Keep prompt deterministic + small enough for a tutorial demo.
    return (
        "You write compelling YouTube story titles.\n\n"
        f"Approved synopsis: {synopsis}\n"
        + (f"Subject/premise: {subject}\n" if subject else "")
        + (f"Genre: {genre}\n" if genre else "")
        + (f"Audience: {age_group}\n" if age_group else "")
        + (f"Target length: {runtime}\n" if runtime else "")
        + "\n"
        "Return ONLY a single short title (no quotes, no headings).\n"
        "Constraints: under 80 characters; punchy and specific; suitable for general audiences."
    )


def _build_description_prompt(content: ContentItem) -> str:
    """Assemble the prompt that asks OpenAI for a YouTube video description."""

    subject = content.subject or ""
    genre = content.genre or ""
    age_group = content.age_group or ""
    runtime = (
        f"{content.video_length_minutes} minute(s)"
        if content.video_length_minutes is not None
        else ""
    )
    synopsis = (content.synopsis or "").strip()
    title = (content.title or "").strip()
    target_words = (
        str(content.target_word_count) if content.target_word_count is not None else ""
    )

    # Return only description text; no markdown headings or bullet lists.
    return (
        "You write YouTube video descriptions for AI story narration.\n\n"
        f"Title: {title}\n"
        f"Approved synopsis: {synopsis}\n"
        + (f"Subject/premise: {subject}\n" if subject else "")
        + (f"Genre: {genre}\n" if genre else "")
        + (f"Audience: {age_group}\n" if age_group else "")
        + (f"Target length: {runtime}\n" if runtime else "")
        + (f"Target script word count: {target_words}\n" if target_words else "")
        + "\n"
        "Return ONLY a description of 2–4 paragraphs. "
        "Include a clear hook plus what viewers will experience. "
        "No hashtags."
    )


def run_generate_title(
    *,
    client: OpenAI,
    model: str,
    content: ContentItem,
    max_attempts: int = 2,
    db: Session | None = None,
    user_id: int | None = None,
) -> GenerateTitleResponse:
    """Generate a YouTube title for the given content item via OpenAI."""

    def _create():
        """Call OpenAI to generate a title from the content prompt."""

        return client.responses.create(
            model=model,
            input=_build_title_prompt(content),
        )

    def _after_attempt(
        attempt: int,
        latency_ms: float,
        exc: BaseException | None,
        result: Any | None,
    ) -> None:
        """Log the title-generation model call to the database."""

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
            purpose="title",
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

    raw = (getattr(resp, "output_text", None) or "").strip()
    if not raw:
        raise RuntimeError("OpenAI returned empty title output")

    # In case the model returns multiple lines, pick the first non-empty line.
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    text = (lines[0] if lines else raw).strip()

    if len(text) > _MAX_OUTPUT_CHARS:
        text = text[: _MAX_OUTPUT_CHARS - 1] + "…"

    content.title = text
    content.status = "title_generated"

    return GenerateTitleResponse(
        content_id=content.id,
        title=text,
        status=content.status,
        attempts_used=attempts_used,
        openai_response_id=getattr(resp, "id", None),
    )


def run_generate_description(
    *,
    client: OpenAI,
    model: str,
    content: ContentItem,
    max_attempts: int = 2,
    db: Session | None = None,
    user_id: int | None = None,
) -> GenerateDescriptionResponse:
    """Generate a YouTube description for the given content item via OpenAI."""

    def _create():
        """Call OpenAI to generate a description from the content prompt."""

        return client.responses.create(
            model=model,
            input=_build_description_prompt(content),
        )

    def _after_attempt(
        attempt: int,
        latency_ms: float,
        exc: BaseException | None,
        result: Any | None,
    ) -> None:
        """Log the description-generation model call to the database."""

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
            purpose="description",
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
        raise RuntimeError("OpenAI returned empty description output")

    if len(text) > _MAX_OUTPUT_CHARS:
        text = text[: _MAX_OUTPUT_CHARS - 1] + "…"

    content.description = text
    content.status = "description_generated"

    return GenerateDescriptionResponse(
        content_id=content.id,
        description=text,
        status=content.status,
        attempts_used=attempts_used,
        openai_response_id=getattr(resp, "id", None),
    )

