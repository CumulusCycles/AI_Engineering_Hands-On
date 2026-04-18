from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GenerateSynopsisResponse(BaseModel):
    """Normalized synopsis generation response."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "content_id": 1,
                    "synopsis": "A shy fox learns to sing at the forest talent show…",
                    "status": "synopsis_generated",
                    "attempts_used": 1,
                    "openai_response_id": "resp_123",
                }
            ],
        },
    )

    content_id: int
    synopsis: str
    status: str
    attempts_used: int = Field(ge=1)
    openai_response_id: str | None = None


class GenerateTitleResponse(BaseModel):
    """Normalized title generation response."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "content_id": 1,
                    "title": "A Shy Fox Sings at the Forest Talent Show",
                    "status": "title_generated",
                    "attempts_used": 1,
                    "openai_response_id": "resp_123",
                }
            ],
        },
    )

    content_id: int
    title: str
    status: str
    attempts_used: int = Field(ge=1)
    openai_response_id: str | None = None


class GenerateDescriptionResponse(BaseModel):
    """Normalized description generation response."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "content_id": 1,
                    "description": "In this cozy story, a shy fox finds its voice ...",
                    "status": "description_generated",
                    "attempts_used": 1,
                    "openai_response_id": "resp_123",
                }
            ],
        },
    )

    content_id: int
    description: str
    status: str
    attempts_used: int = Field(ge=1)
    openai_response_id: str | None = None


class ApproveStepRequest(BaseModel):
    """Approve currently generated step text (Synopsis/Title/Description)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"step": "synopsis"}, {"step": "title"}, {"step": "description"}],
        },
    )

    step: Literal["synopsis", "title", "description"]


class RegenerateStepRequest(BaseModel):
    """Regenerate currently generated step text (Synopsis/Title/Description)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"step": "synopsis"}, {"step": "title"}, {"step": "description"}],
        },
    )

    step: Literal["synopsis", "title", "description"]

