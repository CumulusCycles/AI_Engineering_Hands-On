from __future__ import annotations

import base64
import re
from io import BytesIO
from typing import Any

from openai import OpenAI
from PIL import Image
from sqlalchemy.orm import Session

from app.db.models import ContentItem
from app.db.repos.model_calls import insert_model_call
from app.schemas.thumbnail_generation import GenerateThumbnailResponse
from app.services.openai_retry import call_with_transient_retry

_SUPPORTED_IMAGE_SIZES: frozenset[str] = frozenset({"1024x1024", "1792x1024", "1024x1792"})


def _build_thumbnail_prompt(content: ContentItem) -> str:
    """Assemble the image-generation prompt for a YouTube thumbnail."""

    title = (content.title or "").strip()
    description = (content.description or "").strip()
    genre = (content.genre or "").strip()
    story = (content.story_text or "").strip()
    story_snippet = story[:1200]

    return (
        "Create a YouTube thumbnail image.\n\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        + (f"Genre: {genre}\n" if genre else "")
        + "\n"
        "Story excerpt (for mood only):\n"
        f"{story_snippet}\n\n"
        "Constraints:\n"
        "- 16:9 composition (thumbnail-friendly).\n"
        "- Bold, readable, high-contrast.\n"
        "- Avoid small text.\n"
        "- No watermarks.\n"
        "- No explicit violence, hate, or sexual content.\n"
    )


def _parse_size(size: str) -> tuple[int, int] | None:
    """Parse a 'WxH' size string into (width, height) or return None if invalid."""

    m = re.fullmatch(r"(\d{2,5})x(\d{2,5})", (size or "").strip())
    if not m:
        return None
    w = int(m.group(1))
    h = int(m.group(2))
    if w < 16 or h < 16:
        return None
    return w, h


def _resize_png(image_bytes: bytes, *, target_size: str) -> bytes:
    """Resize a PNG image to the given 'WxH' dimensions using Lanczos resampling."""

    parsed = _parse_size(target_size)
    if parsed is None:
        return image_bytes
    target_w, target_h = parsed
    with Image.open(BytesIO(image_bytes)) as im:
        # Ensure a consistent mode; keep PNG output.
        im2 = im.convert("RGBA")
        im2 = im2.resize((target_w, target_h), resample=Image.Resampling.LANCZOS)
        out = BytesIO()
        im2.save(out, format="PNG", optimize=True)
        return out.getvalue()


def _decode_first_b64_image(resp: Any) -> bytes:
    """Extract and base64-decode the first image from an OpenAI image response."""

    data = getattr(resp, "data", None)
    if not data or not isinstance(data, list) or len(data) < 1:
        raise RuntimeError("OpenAI image response had no data")
    first = data[0]
    b64 = getattr(first, "b64_json", None)
    if b64 is None:
        raise RuntimeError("OpenAI image response missing b64_json")
    try:
        return base64.b64decode(str(b64), validate=False)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("Failed to decode OpenAI image base64") from exc


def run_generate_thumbnail(
    *,
    client: OpenAI,
    model_image: str,
    size: str,
    quality: str,
    style: str,
    content: ContentItem,
    max_attempts: int = 2,
    db: Session | None = None,
    user_id: int | None = None,
) -> tuple[GenerateThumbnailResponse, bytes]:
    """Generate a thumbnail image via OpenAI and return the response with raw PNG bytes."""

    def _after_attempt(
        attempt: int,
        latency_ms: float,
        exc: BaseException | None,
        result: Any | None,
    ) -> None:
        """Log the image-generation model call to the database."""

        if db is None or user_id is None:
            return
        ok = exc is None and result is not None
        err: str | None = None
        resolved_model = model_image
        if ok and result is not None:
            resolved_model = getattr(result, "model", None) or model_image
        if exc is not None:
            err = type(exc).__name__
        insert_model_call(
            db,
            user_id=user_id,
            operation_type="images_generate",
            model_name=str(resolved_model),
            purpose="thumbnail",
            attempt_index=attempt,
            success=ok,
            latency_ms=max(0, int(round(latency_ms))),
            token_input=None,
            token_output=None,
            error_type=err,
        )

    def _do_generate():
        """Call the OpenAI images API with the thumbnail prompt and configured settings."""

        prompt = _build_thumbnail_prompt(content)
        requested_size = (size or "").strip()
        api_size = requested_size if requested_size in _SUPPORTED_IMAGE_SIZES else "1792x1024"
        return client.images.generate(
            model=model_image,
            prompt=prompt,
            # Request base64 so we can persist bytes in SQLite.
            response_format="b64_json",
            size=api_size,
            quality=quality,
            style=style,
        )

    resp, attempts_used = call_with_transient_retry(
        _do_generate,
        max_attempts=max_attempts,
        after_attempt=_after_attempt,
    )

    image_bytes = _decode_first_b64_image(resp)
    # Some models only support specific sizes. If the requested size isn't supported,
    # generate at a supported size then downscale to the requested thumbnail dimensions.
    if (size or "").strip() not in _SUPPORTED_IMAGE_SIZES:
        image_bytes = _resize_png(image_bytes, target_size=size)
    mime = "image/png"
    openai_id = getattr(resp, "id", None)
    b64_out = base64.b64encode(image_bytes).decode("ascii")

    return (
        GenerateThumbnailResponse(
            content_id=content.id,
            status="thumbnail_generated",
            attempts_used=attempts_used,
            thumbnail_mime_type=mime,
            thumbnail_bytes_base64=b64_out,
            openai_image_response_id=openai_id,
        ),
        image_bytes,
    )

