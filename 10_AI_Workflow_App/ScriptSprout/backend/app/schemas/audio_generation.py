from __future__ import annotations

from base64 import b64encode
from typing import Literal

from pydantic import BaseModel, Field


class GenerateAudioRequest(BaseModel):
    voice_key: Literal["female_us", "female_uk", "male_us", "male_uk"] | None = None


class GenerateAudioResponse(BaseModel):
    content_id: int
    status: Literal["audio_generated"]
    attempts_used: int = Field(ge=1)
    audio_mime_type: str = "audio/mpeg"
    audio_voice: str
    audio_bytes_base64: str
    openai_audio_response_id: str | None = None

    @classmethod
    def from_bytes(
        cls,
        *,
        content_id: int,
        attempts_used: int,
        audio_voice: str,
        audio_bytes: bytes,
        openai_audio_response_id: str | None,
    ) -> GenerateAudioResponse:
        """Build a response with base64-encoded audio from raw bytes."""

        return cls(
            content_id=content_id,
            status="audio_generated",
            attempts_used=attempts_used,
            audio_voice=audio_voice,
            audio_bytes_base64=b64encode(audio_bytes).decode("ascii"),
            openai_audio_response_id=openai_audio_response_id,
        )
