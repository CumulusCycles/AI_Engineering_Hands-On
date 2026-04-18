"""Structured story parameters from NLP prompts + follow-up UI hints."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FollowUpInputKind = Literal["text", "number", "single_select"]


class ExtractStoryParametersRequest(BaseModel):
    """Author sends a free-form prompt; the model extracts structured fields."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "prompt": (
                        "A 12-minute cozy fantasy bedtime story for kids ages 6–8 "
                        "about a shy fox who learns to sing."
                    ),
                },
            ],
        },
    )

    prompt: str = Field(
        min_length=1,
        max_length=8_000,
        description="Natural-language idea for a YouTube story video.",
    )


class StoryParametersParsed(BaseModel):
    """JSON schema shape for `responses.parse` (model output)."""

    model_config = ConfigDict(extra="ignore")

    subject: str | None = Field(
        default=None,
        description="Core premise or main character/conflict in a short phrase.",
    )
    genre: str | None = Field(
        default=None,
        description="Fiction genre (e.g. fantasy, science_fiction, mystery, adventure).",
    )
    age_group: str | None = Field(
        default=None,
        description="Audience band: kids, tween, teen, young_adult, adult, or all_ages.",
    )
    video_length_minutes: int | None = Field(
        default=None,
        description="Target video runtime in whole minutes (1–120) if inferable.",
    )
    target_word_count: int | None = Field(
        default=None,
        description="Optional approximate story word count if the user specified length.",
    )
    missing_fields: list[str] = Field(
        default_factory=list,
        description=(
            "Which of subject, genre, age_group, video_length_minutes, target_word_count "
            "could not be inferred (use exact snake_case names)."
        ),
    )


class MissingFieldFollowUp(BaseModel):
    """One UI-ready follow-up for a missing slot."""

    field: str = Field(description="Canonical name: subject, genre, age_group, …")
    question: str = Field(description="Short question to show the author.")
    input_kind: FollowUpInputKind = Field(
        description="Suggested control: free text, integer, or single-select.",
    )
    guidance: str | None = Field(
        default=None,
        description="Optional helper text (format hints, examples).",
    )
    suggested_options: list[str] | None = Field(
        default=None,
        description="For single_select; server-provided labels/slugs for pickers.",
    )


class StoryParametersExtractResponse(BaseModel):
    """Normalized extraction result returned to the API client."""

    subject: str | None = None
    genre: str | None = None
    age_group: str | None = None
    video_length_minutes: int | None = None
    target_word_count: int | None = None
    missing_fields: list[str] = Field(default_factory=list)
    is_complete: bool = Field(
        description="True when subject, genre, age_group, and video_length_minutes are all set.",
    )
    follow_up: list[MissingFieldFollowUp] = Field(
        default_factory=list,
        description="One entry per name in missing_fields; empty when nothing is missing.",
    )
    attempts_used: int = Field(ge=1)
    openai_response_id: str | None = None
