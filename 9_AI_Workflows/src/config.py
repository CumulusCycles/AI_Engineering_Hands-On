"""Application configuration — frozen Pydantic model loaded from the environment."""

from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field


_DEFAULT_BASE_MODEL = "gpt-5-nano"

class AppConfig(BaseModel):
    """
    Immutable runtime configuration for the video content generator application.

    Use AppConfig.from_env() to load from .env / os.environ. The model resolution chain (synopsis → title/description fallbacks)
    is applied at construction time so callers always get the resolved id.

    Attributes:
        base_model (str): The base model name.
        model_synopsis (str): Model for synopsis generation.
        model_title (str): Model for title generation.
        model_description (str): Model for description generation.
        model_story (str): Model for story generation.
        model_story_guard (str): Model for story guardrails check.
        model_thumbnail_image (str): Model for thumbnail image generation.
        model_thumbnail_text_check (str): Model for thumbnail text-detection check.
        thumbnail_size (Literal): Thumbnail image size.
        thumbnail_quality (Literal): Thumbnail image quality.
        max_story_gen (int): Maximum number of story generations on guardrails failure.
        max_thumbnail_gen (int): Maximum thumbnail generation attempts when text is detected.
        output_dir (str): Output directory.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    base_model: str = Field(default=_DEFAULT_BASE_MODEL)
    model_synopsis: str
    model_title: str
    model_description: str
    model_story: str
    model_story_guard: str

    model_thumbnail_image: str = Field(default="gpt-image-1-mini")
    model_thumbnail_text_check: str
    thumbnail_size: Literal["auto", "1024x1024", "1536x1024", "1024x1536"] = Field(
        default="1536x1024",
    )
    thumbnail_quality: Literal["auto", "low", "medium", "high"] = Field(default="low")

    max_story_gen: int = Field(default=2, ge=1)
    max_thumbnail_gen: int = Field(default=2, ge=1)

    output_dir: str = Field(default="output")

    # @classmethod indicates this method is called on the class (AppConfig.from_env()),
    # not on an instance.
    # `cls` is the class object, so `cls(...)` constructs and returns that class
    # (or a subclass if inherited), rather than hardcoding AppConfig(...).
    # This pattern makes from_env() a class-level factory for validated config objects.
    @classmethod
    def from_env(cls) -> AppConfig:
        """Load from ``.env`` + ``os.environ`` with the documented fallback chain."""
        load_dotenv()

        def env(name: str) -> str | None:
            raw = os.environ.get(name)
            return raw.strip() if raw and raw.strip() else None

        base = env("BASE_MODEL") or _DEFAULT_BASE_MODEL
        synopsis = env("MODEL_SYNOPSIS") or base

        raw_max = env("MAX_STORY_GEN")
        try:
            max_gen = max(1, int(raw_max)) if raw_max else 2
        except ValueError:
            max_gen = 2
        raw_max_thumbnail = env("MAX_THUMBNAIL_GEN")
        try:
            max_thumbnail_gen = max(1, int(raw_max_thumbnail)) if raw_max_thumbnail else 2
        except ValueError:
            max_thumbnail_gen = 2

        # return the class with the values from the environment variables
        return cls(
            base_model=base,
            model_synopsis=synopsis,
            model_title=env("MODEL_TITLE") or synopsis,
            model_description=env("MODEL_DESCRIPTION") or synopsis,
            model_story=env("MODEL_STORY") or base,
            model_story_guard=env("MODEL_STORY_GUARD") or base,
            model_thumbnail_image=env("MODEL_THUMBNAIL_IMAGE") or "gpt-image-1-mini",
            model_thumbnail_text_check=env("MODEL_THUMBNAIL_TEXT_CHECK") or base,
            thumbnail_size=env("THUMBNAIL_SIZE") or "1536x1024",  # type: ignore[arg-type]
            thumbnail_quality=env("THUMBNAIL_QUALITY") or "low",  # type: ignore[arg-type]
            max_story_gen=max_gen,
            max_thumbnail_gen=max_thumbnail_gen,
            output_dir=env("OUTPUT_DIR") or "output",
        )
