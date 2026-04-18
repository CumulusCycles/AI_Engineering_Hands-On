from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GuardrailsCheckParsed(BaseModel):
    """Structured guardrails check result."""

    passed: bool
    failure_reason: str | None = None


class GenerateStoryResponse(BaseModel):
    """Normalized story generation + guardrails parse response."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "content_id": 1,
                    "story_text": "Once upon a time ...",
                    "status": "guardrails_passed",
                    "story_attempts_used": 1,
                    "guardrails_attempts_used": 1,
                    "openai_story_response_id": "resp_story_1",
                    "openai_guardrails_response_id": "resp_guard_1",
                }
            ],
        },
    )

    content_id: int
    story_text: str
    status: Literal["guardrails_passed", "guardrails_failed", "story_generated"]

    story_attempts_used: int = Field(ge=1)
    guardrails_attempts_used: int = Field(ge=0)

    generation_run_id: int | None = None

    openai_story_response_id: str | None = None
    openai_guardrails_response_id: str | None = None

