"""Deterministic follow-up prompts for incomplete parameter extraction."""

from __future__ import annotations

from app.schemas.story_parameters import MissingFieldFollowUp

_FIELD_ORDER = (
    "subject",
    "genre",
    "age_group",
    "video_length_minutes",
    "target_word_count",
)

_GENRE_OPTIONS: tuple[str, ...] = (
    "fantasy",
    "science_fiction",
    "mystery",
    "adventure",
    "horror",
    "romance",
    "historical_fiction",
    "other",
)

_AGE_OPTIONS: tuple[str, ...] = (
    "kids",
    "tween",
    "teen",
    "young_adult",
    "adult",
    "all_ages",
)


def build_missing_field_follow_ups(missing_fields: list[str]) -> list[MissingFieldFollowUp]:
    """Generate user-facing follow-up prompts for each missing story parameter field."""

    want = set(missing_fields)
    out: list[MissingFieldFollowUp] = []

    for field in _FIELD_ORDER:
        if field not in want:
            continue
        if field == "subject":
            out.append(
                MissingFieldFollowUp(
                    field=field,
                    question="What is the main idea, character, or conflict for this video?",
                    input_kind="text",
                    guidance="A short phrase is fine (this becomes the working subject).",
                ),
            )
        elif field == "genre":
            out.append(
                MissingFieldFollowUp(
                    field=field,
                    question="Which genre fits best?",
                    input_kind="single_select",
                    guidance="Pick the closest match; you can refine later.",
                    suggested_options=list(_GENRE_OPTIONS),
                ),
            )
        elif field == "age_group":
            out.append(
                MissingFieldFollowUp(
                    field=field,
                    question="Who is the primary audience?",
                    input_kind="single_select",
                    guidance="Choose the band that best matches tone and reading level.",
                    suggested_options=list(_AGE_OPTIONS),
                ),
            )
        elif field == "video_length_minutes":
            out.append(
                MissingFieldFollowUp(
                    field=field,
                    question="How long should the finished video be?",
                    input_kind="number",
                    guidance="Whole minutes, typically between 1 and 120.",
                ),
            )
        elif field == "target_word_count":
            out.append(
                MissingFieldFollowUp(
                    field=field,
                    question="Roughly how many words should the story be?",
                    input_kind="number",
                    guidance="Optional; only needed if you care about script length.",
                ),
            )

    return out
