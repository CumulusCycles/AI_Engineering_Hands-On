from __future__ import annotations

from typing import Any

from openai import OpenAI
from sqlalchemy.orm import Session

from app.db.repos.model_calls import insert_model_call
from app.schemas.openai_smoke import OpenAiSmokeResponse
from app.services.openai_helpers import usage_tokens as _usage_tokens
from app.services.openai_retry import call_with_transient_retry

_MAX_OUTPUT_CHARS = 16_000


def _usage_dict(resp: Any) -> dict | None:
    """Extract the usage object from an OpenAI response as a plain dict."""

    u = getattr(resp, "usage", None)
    if u is None:
        return None
    md = getattr(u, "model_dump", None)
    if not callable(md):
        return None
    raw = md(mode="json", exclude_none=True)
    return raw if isinstance(raw, dict) else None


def run_responses_smoke(
    *,
    client: OpenAI,
    model: str,
    user_prompt: str,
    max_attempts: int = 2,
    db: Session | None = None,
    user_id: int | None = None,
) -> OpenAiSmokeResponse:
    """Send a simple prompt via OpenAI responses.create and return the smoke-test result."""

    def _create():
        """Call OpenAI responses.create with the user prompt."""
        return client.responses.create(model=model, input=user_prompt)

    def _after_attempt(
        attempt: int,
        latency_ms: float,
        exc: BaseException | None,
        result: Any | None,
    ) -> None:
        """Log each smoke-test attempt to the model_calls table."""

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
            model_name=resolved_model,
            purpose="admin_openai_smoke",
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
    if len(text) > _MAX_OUTPUT_CHARS:
        text = text[: _MAX_OUTPUT_CHARS - 1] + "…"

    usage = _usage_dict(resp)

    return OpenAiSmokeResponse(
        response_id=resp.id,
        model=resp.model or model,
        output_text=text,
        status=resp.status or "unknown",
        usage=usage,
        attempts_used=attempts_used,
    )
