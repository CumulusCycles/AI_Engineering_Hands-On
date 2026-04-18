"""OpenAI Responses API and Images API client helpers."""

import base64
import os
import sys
import time
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Literal, TypeVar

from openai import APIConnectionError, APITimeoutError, InternalServerError, OpenAI, RateLimitError

from .schemas import GuardrailsCheckResult

T = TypeVar("T")

_MAX_RETRIES = 3
_INITIAL_BACKOFF = 1.0


def _with_retry(fn: Callable[[], T]) -> T:
    """Execute *fn*, retrying on transient OpenAI errors with exponential backoff."""
    backoff = _INITIAL_BACKOFF
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            return fn()
        except (RateLimitError, APIConnectionError, APITimeoutError, InternalServerError) as exc:
            if attempt == _MAX_RETRIES:
                raise
            print(
                f"  Transient API error ({type(exc).__name__}), "
                f"retrying in {backoff:.0f}s (attempt {attempt}/{_MAX_RETRIES})…",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(backoff)
            backoff *= 2
    raise AssertionError("unreachable")


def create_client() -> OpenAI:
    """Return an OpenAI client configured from the environment.

    Reads OPENAI_API_KEY and related settings (see OpenAI SDK docs).
    Fails fast with a clear message if the key is missing.

    Returns:
        A new OpenAI client instance.
    """
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise SystemExit(
            "Error: OPENAI_API_KEY is not set. "
            "Add it to your .env file or export it in your shell."
        )
    return OpenAI()


def generate_text(
    client: OpenAI,
    instructions: str,
    user_prompt: str,
    *,
    model: str,
    purpose: str | None = None,
) -> str:
    """Call responses.create and return the assistant text.

    Args:
        client: Authenticated OpenAI client.
        instructions: System-style instructions (role, guardrails, etc.).
        user_prompt: User message for this turn.
        model: Model id for this request (see the models module for per-step ids).
        purpose: Short label for stderr (e.g. ``\"synopsis\"``); shown after the model id.

    Returns:
        The response output_text string.
    """
    suffix = f" ({purpose})" if purpose else ""
    print(f"Using model: {model}{suffix}", file=sys.stderr, flush=True)
    response = _with_retry(
        lambda: client.responses.create(
            model=model,
            instructions=instructions,
            input=user_prompt,
        )
    )
    return response.output_text


def guardrails_check(
    client: OpenAI,
    instructions: str,
    user_prompt: str,
    *,
    model: str,
    purpose: str | None = "guardrails check",
) -> tuple[bool, str]:
    """Review story text via ``responses.parse`` + ``GuardrailsCheckResult`` schema.

    The caller is responsible for building the instructions and prompt (see
    ``prompts.build_guardrails_check_prompt``).
    """
    suffix = f" ({purpose})" if purpose else ""
    print(f"Using model: {model}{suffix}", file=sys.stderr, flush=True)
    response = _with_retry(
        lambda: client.responses.parse(
            model=model,
            instructions=instructions,
            input=user_prompt,
            text_format=GuardrailsCheckResult,
        )
    )
    parsed = response.output_parsed
    if parsed is None:
        return False, "guardrails response had no parsed structured output"
    if parsed.passed:
        return True, ""
    reason = parsed.failure_reason.strip()
    return False, reason or "unspecified"


def generate_youtube_thumbnail(
    client: OpenAI,
    *,
    prompt: str,
    model: str,
    size: Literal["auto", "1024x1024", "1536x1024", "1024x1536"],
    output_path: str,
    quality: Literal["auto", "low", "medium", "high"] = "low",
) -> str:
    """Call ``images.generate`` (POST ``/v1/images/generations``), save PNG bytes, return path.

    Intended for GPT Image models (for example ``gpt-image-1-mini``) using Images API.
    """
    print(
        f"Images API: model={model} size={size} quality={quality}",
        file=sys.stderr,
        flush=True,
    )
    response = _with_retry(
        lambda: client.images.generate(
            model=model,
            prompt=prompt,
            n=1,
            size=size,
            quality=quality,
        )
    )
    if not response.data:
        raise RuntimeError("Image generation returned no data")
    first = response.data[0]
    if first.b64_json:
        raw = base64.b64decode(first.b64_json)
    elif first.url:
        with urllib.request.urlopen(first.url) as resp:
            raw = resp.read()
    else:
        raise RuntimeError("Image generation returned neither b64_json nor url payload")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    return str(out.resolve())


def thumbnail_has_visible_text(
    client: OpenAI,
    *,
    image_path: str,
    model: str,
    purpose: str | None = "thumbnail text check",
) -> bool | None:
    """Return whether an image appears to contain visible text.

    Uses a vision-capable Responses model to classify a generated thumbnail as:
    ``TEXT_PRESENT`` or ``NO_TEXT``.

    Returns ``None`` if the check cannot run (for example, model capability or API error).
    """
    suffix = f" ({purpose})" if purpose else ""
    print(f"Using model: {model}{suffix}", file=sys.stderr, flush=True)
    try:
        raw = Path(image_path).read_bytes()
        b64 = base64.b64encode(raw).decode("ascii")
        response = _with_retry(
            lambda: client.responses.create(
                model=model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": (
                                    "Check this image and decide whether any visible text appears anywhere "
                                    "(letters, words, numbers, logos with readable characters, watermarks, labels). "
                                    "Reply with exactly one token: TEXT_PRESENT or NO_TEXT."
                                ),
                            },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/png;base64,{b64}",
                            },
                        ],
                    }
                ],
            )
        )
        answer = (response.output_text or "").strip().upper()
        if "TEXT_PRESENT" in answer:
            return True
        if "NO_TEXT" in answer:
            return False
        return None
    except Exception as exc:
        print(
            f"  Thumbnail text check unavailable ({type(exc).__name__}: {exc}). "
            "Proceeding without text validation.",
            file=sys.stderr,
            flush=True,
        )
        return None
