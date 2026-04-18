from __future__ import annotations

from openai import OpenAI

from app.config import Settings


def build_openai_client(settings: Settings) -> OpenAI:
    """Create an OpenAI client from the configured API key."""

    key = settings.openai_api_key
    if key is None or not str(key).strip():
        msg = "OpenAI API key is not configured"
        raise ValueError(msg)
    return OpenAI(api_key=str(key).strip())
