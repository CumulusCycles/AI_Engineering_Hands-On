"""Story generation + guardrails parse via OpenAI Responses API."""

from __future__ import annotations

from typing import Any

from openai import OpenAI
from sqlalchemy.orm import Session

from app.db.models import ContentItem
from app.db.repos.generation_runs import (
    insert_generation_run,
    insert_guardrails_event,
    update_generation_run_after_story_and_guardrails,
)
from app.db.repos.model_calls import insert_model_call
from app.schemas.story_generation import GenerateStoryResponse, GuardrailsCheckParsed
from app.services.openai_helpers import usage_tokens as _usage_tokens
from app.services.openai_retry import call_with_transient_retry

_MAX_OUTPUT_CHARS = 20_000

_GUARDRAILS_INSTRUCTIONS = (
    "You are a story safety / quality guardrails checker.\n"
    "Rules:\n"
    "- If the story is suitable for the specified audience (age_group) "
    "and free of obvious policy issues, return passed=true.\n"
    "- Otherwise return passed=false and a short failure_reason explaining why.\n"
    "- Return ONLY the structured result.\n"
)


def _build_story_prompt(content: ContentItem, *, failure_reason: str | None = None) -> str:
    """Assemble the story-writing prompt from content metadata and optional guardrails feedback."""

    subject = content.subject or ""
    genre = content.genre or ""
    age_group = content.age_group or ""
    synopsis = (content.synopsis or "").strip()
    title = (content.title or "").strip()
    description = (content.description or "").strip()

    runtime = (
        f"{content.video_length_minutes} minute(s)"
        if content.video_length_minutes is not None
        else ""
    )
    target_words = (
        f"{content.target_word_count} words" if content.target_word_count is not None else ""
    )

    # Keep this deterministic-ish for tutorial output. Avoid headings/bullets.
    return (
        "Write a complete YouTube narration story.\n\n"
        f"Title: {title}\n"
        f"Approved synopsis: {synopsis}\n"
        f"Description: {description}\n"
        + (f"Subject/premise: {subject}\n" if subject else "")
        + (f"Genre: {genre}\n" if genre else "")
        + (f"Audience: {age_group}\n" if age_group else "")
        + (f"Target length: {runtime}\n" if runtime else "")
        + (f"Target word count: {target_words}\n" if target_words else "")
        + "\n"
        "Constraints:\n"
        "- Return ONLY story text suitable to read aloud.\n"
        "- Use vivid but simple language.\n"
        "- Do not include meta commentary or hashtags.\n"
        + (f"\nGuardrails feedback to address:\n- {failure_reason}\n" if failure_reason else "")
    )


def _build_guardrails_input(content: ContentItem, story_text: str) -> str:
    """Format the guardrails checker input with audience age group and story text."""

    age_group = content.age_group or ""
    return (
        "Audience age_group:\n"
        f"{age_group}\n\n"
        "Story:\n"
        f"{story_text}\n"
    )


def run_generate_story_and_guardrails(  # noqa: C901
    *,
    client: OpenAI,
    model_story: str,
    model_guardrails: str,
    content: ContentItem,
    max_attempts: int = 2,
    db: Session | None = None,
    user_id: int | None = None,
) -> GenerateStoryResponse:
    """Generate a story via OpenAI, optionally running guardrails checks in a retry loop."""

    def _after_create(
        attempt: int,
        latency_ms: float,
        exc: BaseException | None,
        result: Any | None,
    ) -> None:
        """Log the story-creation model call to the database."""

        if db is None or user_id is None:
            return
        ok = exc is None and result is not None
        ti, to = (None, None)
        err: str | None = None
        resolved_model = model_story
        if ok and result is not None:
            ti, to = _usage_tokens(result)
            resolved_model = getattr(result, "model", None) or model_story
        if exc is not None:
            err = type(exc).__name__
        insert_model_call(
            db,
            user_id=user_id,
            operation_type="responses_create",
            model_name=str(resolved_model),
            purpose="story",
            attempt_index=attempt,
            success=ok,
            latency_ms=max(0, int(round(latency_ms))),
            token_input=ti,
            token_output=to,
            error_type=err,
        )

    def _after_guardrails_parse(
        attempt: int,
        latency_ms: float,
        exc: BaseException | None,
        result: Any | None,
    ) -> None:
        """Log the guardrails-parse model call to the database."""

        if db is None or user_id is None:
            return
        ok = exc is None and result is not None
        ti, to = (None, None)
        err: str | None = None
        resolved_model = model_guardrails
        if ok and result is not None:
            ti, to = _usage_tokens(result)
            resolved_model = getattr(result, "model", None) or model_guardrails
        if exc is not None:
            err = type(exc).__name__
        insert_model_call(
            db,
            user_id=user_id,
            operation_type="responses_parse",
            model_name=str(resolved_model),
            purpose="guardrails_check",
            attempt_index=attempt,
            success=ok,
            latency_ms=max(0, int(round(latency_ms))),
            token_input=ti,
            token_output=to,
            error_type=err,
        )

    def _parse_guardrails(story_text: str):
        """Send the story to the guardrails model and return the parsed safety check."""

        return client.responses.parse(
            model=model_guardrails,
            input=_build_guardrails_input(content, story_text),
            text_format=GuardrailsCheckParsed,
            instructions=_GUARDRAILS_INSTRUCTIONS,
        )

    max_loops = max(1, int(content.guardrails_max_loops or 1))

    generation_run_id: int | None = None
    if db is not None and user_id is not None:
        # Create a run record up-front so we can attach per-attempt guardrails events.
        gen_run = insert_generation_run(
            db,
            user_id=user_id,
            content_id=content.id,
            status="story_generated",
        )
        generation_run_id = gen_run.id

    story_attempts_used = 0
    guardrails_attempts_used = 0
    status: str = "story_generated"
    story_text: str = ""
    failure_reason: str | None = None
    openai_story_response_id: str | None = None
    openai_guardrails_response_id: str | None = None

    for loop_idx in range(max_loops):
        story_attempts_used += 1

        # Include guardrails feedback after the first failed check.
        def _create_story_with_feedback():
            """Call OpenAI to generate the story, incorporating any prior guardrails feedback."""

            prompt = _build_story_prompt(content, failure_reason=failure_reason)
            return client.responses.create(model=model_story, input=prompt)

        story_resp, _transient_story_attempts = call_with_transient_retry(
            _create_story_with_feedback,
            max_attempts=max_attempts,
            after_attempt=_after_create,
        )

        story_text = (getattr(story_resp, "output_text", None) or "").strip()
        if not story_text:
            raise RuntimeError("OpenAI returned empty story output")
        if len(story_text) > _MAX_OUTPUT_CHARS:
            story_text = story_text[: _MAX_OUTPUT_CHARS - 1] + "..."

        openai_story_response_id = getattr(story_resp, "id", None)

        if not content.guardrails_enabled:
            status = "story_generated"
            break

        guardrails_attempts_used += 1

        def _call_guardrails():
            """Run the guardrails safety check on the latest story text."""

            return _parse_guardrails(story_text)

        raw_guardrails_resp, _transient_guardrails_attempts = call_with_transient_retry(
            _call_guardrails,
            max_attempts=max_attempts,
            after_attempt=_after_guardrails_parse,
        )

        parsed_obj = raw_guardrails_resp.output_parsed
        if parsed_obj is None:
            raise RuntimeError("OpenAI guardrails parse returned no structured output")
        if not isinstance(parsed_obj, GuardrailsCheckParsed):
            parsed_obj = GuardrailsCheckParsed.model_validate(parsed_obj)

        openai_guardrails_response_id = getattr(raw_guardrails_resp, "id", None)

        if parsed_obj.passed:
            status = "guardrails_passed"
            if generation_run_id is not None:
                insert_guardrails_event(
                    db,
                    run_id=generation_run_id,
                    attempt_index=guardrails_attempts_used,
                    passed=True,
                    failure_reason=None,
                )
            break

        # Failed -> retry using the guardrails failure feedback.
        failure_reason = parsed_obj.failure_reason or "Guardrails check failed."
        status = "guardrails_failed"
        if generation_run_id is not None:
            insert_guardrails_event(
                db,
                run_id=generation_run_id,
                attempt_index=guardrails_attempts_used,
                passed=False,
                failure_reason=failure_reason,
            )

    content.story_text = story_text
    content.status = status

    if generation_run_id is not None and db is not None:
        final_failure_reason = None
        if status == "guardrails_failed":
            final_failure_reason = failure_reason
        update_generation_run_after_story_and_guardrails(
            db,
            run_id=generation_run_id,
            status=status,
            failure_reason=final_failure_reason,
            story_attempts_used=story_attempts_used,
            guardrails_attempts_used=guardrails_attempts_used,
        )

    return GenerateStoryResponse(
        content_id=content.id,
        story_text=story_text,
        status=status,
        story_attempts_used=story_attempts_used,
        guardrails_attempts_used=guardrails_attempts_used,
        generation_run_id=generation_run_id,
        openai_story_response_id=openai_story_response_id,
        openai_guardrails_response_id=openai_guardrails_response_id,
    )

