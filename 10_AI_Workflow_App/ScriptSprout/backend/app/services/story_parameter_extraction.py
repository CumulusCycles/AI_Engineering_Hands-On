"""Extract structured story parameters via OpenAI `responses.parse`."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from openai import OpenAI
from sqlalchemy.orm import Session

from app.db.repos.model_calls import insert_model_call
from app.schemas.story_parameters import StoryParametersExtractResponse, StoryParametersParsed
from app.services.missing_field_follow_up import build_missing_field_follow_ups
from app.services.openai_helpers import usage_tokens as _usage_tokens
from app.services.openai_retry import call_with_transient_retry

_EXTRACTION_INSTRUCTIONS = (
    "You extract structured metadata for a YouTube story video from the user's message.\n"
    "Rules:\n"
    "- Infer values when implied; list missing_fields only when a value cannot be inferred.\n"
    "- missing_fields use snake_case: subject, genre, age_group, video_length_minutes, "
    "target_word_count.\n"
    "- genre: short slug (fantasy, science_fiction, mystery, adventure, horror, romance, "
    "historical_fiction, other).\n"
    "- age_group: kids, tween, teen, young_adult, adult, or all_ages.\n"
    "- video_length_minutes: whole minutes if duration is given "
    '(e.g. "ten minute video" -> 10).\n'
    "- target_word_count: only if the user specifies words/pages; else null.\n"
    "- subject: one concise phrase (not the full prompt).\n"
)

_CANONICAL_FIELDS = frozenset(
    {"subject", "genre", "age_group", "video_length_minutes", "target_word_count"},
)
_REQUIRED_FOR_COMPLETE = frozenset({"subject", "genre", "age_group", "video_length_minutes"})

_GENRE_ALIASES: dict[str, str] = {
    "sci-fi": "science_fiction",
    "sci fi": "science_fiction",
    "science fiction": "science_fiction",
    "scifi": "science_fiction",
    "sf": "science_fiction",
}

_AGE_ALIASES: dict[str, str] = {
    "child": "kids",
    "children": "kids",
    "elementary": "kids",
    "middle school": "tween",
    "preteen": "tween",
    "teenager": "teen",
    "teenagers": "teen",
    "ya": "young_adult",
    "young adult": "young_adult",
    "grown-ups": "adult",
    "grownups": "adult",
    "general audience": "all_ages",
    "family": "all_ages",
}


@dataclass(frozen=True)
class _Normalized:
    subject: str | None
    genre: str | None
    age_group: str | None
    video_length_minutes: int | None
    target_word_count: int | None


def _clean_str(v: str | None) -> str | None:
    """Strip whitespace from a string, returning None if empty or None."""

    if v is None:
        return None
    s = v.strip()
    return s if s else None


def _normalize_genre(raw: str | None) -> str | None:
    """Normalize a raw genre string to a canonical snake_case slug."""

    s = _clean_str(raw)
    if s is None:
        return None
    key = s.lower().replace("-", " ").strip()
    if key in _GENRE_ALIASES:
        return _GENRE_ALIASES[key]
    slug = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
    return slug if slug else None


def _normalize_age_group(raw: str | None) -> str | None:
    """Normalize a raw age-group string to an allowed canonical slug."""

    s = _clean_str(raw)
    if s is None:
        return None
    key = s.lower().replace("-", " ").strip()
    if key in _AGE_ALIASES:
        return _AGE_ALIASES[key]
    slug = re.sub(r"[^a-z0-9]+", "_", key).strip("_")
    allowed = {"kids", "tween", "teen", "young_adult", "adult", "all_ages"}
    return slug if slug in allowed else None


def _clamp_int(v: int | None, lo: int, hi: int) -> int | None:
    """Clamp an optional integer to the range [lo, hi], returning None on invalid input."""

    if v is None:
        return None
    try:
        n = int(v)
    except (TypeError, ValueError):
        return None
    return max(lo, min(hi, n))


def _normalize_parsed(raw: StoryParametersParsed) -> _Normalized:
    """Normalize all fields of a parsed story-parameters object."""

    return _Normalized(
        subject=_clean_str(raw.subject),
        genre=_normalize_genre(raw.genre),
        age_group=_normalize_age_group(raw.age_group),
        video_length_minutes=_clamp_int(raw.video_length_minutes, 1, 240),
        target_word_count=_clamp_int(raw.target_word_count, 200, 80_000),
    )


def _merge_missing(parsed: StoryParametersParsed, norm: _Normalized) -> list[str]:
    """Merge model-reported missing fields with fields still None after normalization."""

    merged = {m for m in parsed.missing_fields if m in _CANONICAL_FIELDS}
    if norm.subject is None:
        merged.add("subject")
    if norm.genre is None:
        merged.add("genre")
    if norm.age_group is None:
        merged.add("age_group")
    if norm.video_length_minutes is None:
        merged.add("video_length_minutes")
    if norm.subject is not None:
        merged.discard("subject")
    if norm.genre is not None:
        merged.discard("genre")
    if norm.age_group is not None:
        merged.discard("age_group")
    if norm.video_length_minutes is not None:
        merged.discard("video_length_minutes")
    if norm.target_word_count is not None:
        merged.discard("target_word_count")
    return sorted(merged)


def _is_complete(norm: _Normalized) -> bool:
    """Return True if all required story parameters have been extracted."""

    return (
        norm.subject is not None
        and norm.genre is not None
        and norm.age_group is not None
        and norm.video_length_minutes is not None
    )




def run_extract_story_parameters(
    *,
    client: OpenAI,
    model: str,
    user_prompt: str,
    max_attempts: int = 2,
    db: Session | None = None,
    user_id: int | None = None,
) -> StoryParametersExtractResponse:
    """Extract structured story parameters from a user prompt via OpenAI responses.parse."""

    def _parse_once():
        """Call OpenAI responses.parse to extract story parameters."""

        return client.responses.parse(
            model=model,
            input=user_prompt,
            text_format=StoryParametersParsed,
            instructions=_EXTRACTION_INSTRUCTIONS,
        )

    def _after_attempt(
        attempt: int,
        latency_ms: float,
        exc: BaseException | None,
        result: Any | None,
    ) -> None:
        """Log each extraction attempt to the model_calls table."""

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
            operation_type="responses_parse",
            model_name=str(resolved_model),
            purpose="extract_story_parameters",
            attempt_index=attempt,
            success=ok,
            latency_ms=max(0, int(round(latency_ms))),
            token_input=ti,
            token_output=to,
            error_type=err,
        )

    raw_resp, attempts_used = call_with_transient_retry(
        _parse_once,
        max_attempts=max_attempts,
        after_attempt=_after_attempt,
    )

    parsed_obj = raw_resp.output_parsed
    if parsed_obj is None:
        msg = "OpenAI parse returned no structured output"
        raise RuntimeError(msg)

    if not isinstance(parsed_obj, StoryParametersParsed):
        parsed_obj = StoryParametersParsed.model_validate(parsed_obj)

    norm = _normalize_parsed(parsed_obj)
    missing = _merge_missing(parsed_obj, norm)
    # If we filled all required fields, drop them from missing_fields even if the model listed them
    if _is_complete(norm):
        missing = [m for m in missing if m not in _REQUIRED_FOR_COMPLETE]

    follow_up = build_missing_field_follow_ups(missing)

    return StoryParametersExtractResponse(
        subject=norm.subject,
        genre=norm.genre,
        age_group=norm.age_group,
        video_length_minutes=norm.video_length_minutes,
        target_word_count=norm.target_word_count,
        missing_fields=missing,
        is_complete=_is_complete(norm),
        follow_up=follow_up,
        attempts_used=attempts_used,
        openai_response_id=getattr(raw_resp, "id", None),
    )
