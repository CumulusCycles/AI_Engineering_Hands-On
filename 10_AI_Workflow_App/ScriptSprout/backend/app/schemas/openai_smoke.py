from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OpenAiSmokeRequest(BaseModel):
    """Minimal input for the admin OpenAI smoke call."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"prompt": "Reply with only the word: pong."}],
        },
    )

    prompt: str = Field(
        default="Reply with only the word: pong.",
        min_length=1,
        max_length=4_000,
        description="Short user message sent to the Responses API.",
    )


class OpenAiSmokeResponse(BaseModel):
    """Normalized successful smoke response (no raw provider error payloads)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "response_id": "resp_123",
                    "model": "gpt-4o-mini",
                    "output_text": "pong",
                    "status": "completed",
                    "usage": {"input_tokens": 12, "output_tokens": 2},
                    "attempts_used": 1,
                }
            ],
        },
    )

    response_id: str
    model: str
    output_text: str
    status: str
    usage: dict[str, Any] | None = Field(
        default=None,
        description="Token usage when the API returns it; shape may vary by model.",
    )
    attempts_used: int = Field(
        default=1,
        ge=1,
        description="Responses API calls made, including transient retries.",
    )
