from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from openai import OpenAI
from sqlalchemy.orm import Session

from app.db.repos.model_calls import insert_model_call
from app.services.openai_retry import call_with_transient_retry


@dataclass(slots=True)
class AudioGenerationResult:
    audio_bytes: bytes
    attempts_used: int
    openai_response_id: str | None


def _read_audio_bytes(response: Any) -> bytes:
    """Extract raw audio bytes from an OpenAI speech response."""

    if isinstance(response, (bytes, bytearray)):
        data = bytes(response)
    elif hasattr(response, "read") and callable(response.read):
        data = response.read()
    elif hasattr(response, "content"):
        data = bytes(response.content)
    else:
        data = b""
    if not data:
        raise RuntimeError("OpenAI audio response did not include audio bytes")
    return data


def run_generate_audio(
    *,
    db: Session,
    user_id: int,
    story_text: str,
    client: OpenAI,
    model_name: str,
    voice: str,
    max_attempts: int,
) -> AudioGenerationResult:
    """Generate an MP3 narration of story_text via OpenAI TTS with retry."""

    attempts = 0
    response_id: str | None = None

    def _do_generate() -> bytes:
        """Call OpenAI audio.speech.create and return the MP3 bytes."""

        nonlocal attempts, response_id
        attempts += 1
        started = perf_counter()
        success = False
        error_type: str | None = None
        resp: Any | None = None
        try:
            resp = client.audio.speech.create(
                model=model_name,
                voice=voice,
                input=story_text,
                response_format="mp3",
            )
            out = _read_audio_bytes(resp)
            response_id = getattr(resp, "id", None)
            success = True
            return out
        except Exception as exc:
            error_type = exc.__class__.__name__
            raise
        finally:
            latency_ms = int((perf_counter() - started) * 1000)
            insert_model_call(
                db,
                user_id=user_id,
                operation_type="audio_speech_create",
                model_name=model_name,
                purpose="audio_narration",
                attempt_index=attempts,
                success=success,
                latency_ms=latency_ms,
                error_type=error_type,
            )
            db.commit()

    audio_bytes, attempts_used = call_with_transient_retry(
        _do_generate,
        max_attempts=max_attempts,
    )
    return AudioGenerationResult(
        audio_bytes=audio_bytes,
        attempts_used=attempts_used,
        openai_response_id=response_id,
    )
