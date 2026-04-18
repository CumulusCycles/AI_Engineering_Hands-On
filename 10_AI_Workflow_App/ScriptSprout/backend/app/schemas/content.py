from __future__ import annotations

from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.db.models import ContentItem

PROMPT_PREVIEW_MAX_LEN = 200

_CREATE_EXAMPLE = {
    "prompt": "A 10-minute cozy mystery set on a small ferry in the Pacific Northwest.",
    "genre": "mystery",
    "subject": "ferry",
    "guardrails_max_loops": 5,
}


class ContentCreate(BaseModel):
    """Start a content row. Prefer **`prompt`**; **`source_prompt`** is legacy-compatible."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [_CREATE_EXAMPLE]},
    )

    prompt: str | None = Field(
        default=None,
        max_length=50_000,
        description="Primary NLP request (preferred; stored as source_prompt).",
    )
    source_prompt: str | None = Field(
        default=None,
        max_length=50_000,
        description="Legacy alias for the same field as `prompt`.",
    )
    subject: str | None = Field(default=None, max_length=512)
    genre: str | None = Field(default=None, max_length=128)
    age_group: str | None = Field(default=None, max_length=128)
    video_length_minutes: int | None = Field(default=None, ge=0, le=24 * 60)
    target_word_count: int | None = Field(default=None, ge=1, le=1_000_000)
    title: str | None = Field(default=None, max_length=512)
    description: str | None = None
    story_text: str | None = None
    guardrails_enabled: bool = True
    guardrails_max_loops: int = Field(default=3, ge=1, le=20)

    @model_validator(mode="after")
    def coalesce_prompt(self) -> Self:
        """Normalize prompt/source_prompt into a single non-empty prompt field."""

        a = (self.prompt or "").strip()
        b = (self.source_prompt or "").strip()
        text = a or b
        if not text:
            raise ValueError("Provide non-empty `prompt` or `source_prompt`.")
        return self.model_copy(update={"prompt": text, "source_prompt": None})

    def create_kwargs(self) -> dict:
        """Return a dict of keyword arguments suitable for ContentItem creation."""

        return {
            "source_prompt": self.prompt,
            "subject": self.subject,
            "genre": self.genre,
            "age_group": self.age_group,
            "video_length_minutes": self.video_length_minutes,
            "target_word_count": self.target_word_count,
            "title": self.title,
            "description": self.description,
            "story_text": self.story_text,
            "guardrails_enabled": self.guardrails_enabled,
            "guardrails_max_loops": self.guardrails_max_loops,
        }


class ContentListItem(BaseModel):
    """Summary row for list views (no full prompt or story body)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "author_id": 2,
                    "status": "draft",
                    "genre": "mystery",
                    "subject": "ferry",
                    "title": None,
                    "prompt_preview": "A 10-minute cozy mystery set on a small ferry…",
                    "has_thumbnail": False,
                    "has_audio": False,
                    "guardrails_enabled": True,
                    "guardrails_max_loops": 5,
                    "created_at": "2025-01-01T12:00:00Z",
                    "updated_at": "2025-01-01T12:00:00Z",
                }
            ]
        },
    )

    id: int
    author_id: int
    status: str
    genre: str | None
    subject: str | None
    title: str | None
    prompt_preview: str
    has_thumbnail: bool
    has_audio: bool
    guardrails_enabled: bool
    guardrails_max_loops: int
    created_at: datetime
    updated_at: datetime


class ContentListPage(BaseModel):
    items: list[ContentListItem]
    total: int
    limit: int
    offset: int


class ContentItemDetail(BaseModel):
    """Full content row for detail view (no raw BLOBs; use has_* flags)."""

    id: int
    author_id: int
    source_prompt: str
    subject: str | None
    genre: str | None
    age_group: str | None
    video_length_minutes: int | None
    target_word_count: int | None
    title: str | None
    description: str | None
    synopsis: str | None
    story_text: str | None
    status: str
    guardrails_enabled: bool
    guardrails_max_loops: int
    created_at: datetime
    updated_at: datetime
    has_thumbnail: bool
    has_audio: bool
    thumbnail_mime_type: str | None
    audio_mime_type: str | None
    audio_voice: str | None
    audio_generated_at: datetime | None


def build_prompt_preview(text: str, max_len: int = PROMPT_PREVIEW_MAX_LEN) -> str:
    """Truncate prompt text to max_len with an ellipsis suffix if needed."""

    t = text.strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def content_item_to_list_item(row: ContentItem) -> ContentListItem:
    """Convert a ContentItem DB row to a ContentListItem summary schema."""

    return ContentListItem(
        id=row.id,
        author_id=row.author_id,
        status=row.status,
        genre=row.genre,
        subject=row.subject,
        title=row.title,
        prompt_preview=build_prompt_preview(row.source_prompt or ""),
        has_thumbnail=row.thumbnail_blob is not None,
        has_audio=row.audio_blob is not None,
        guardrails_enabled=row.guardrails_enabled,
        guardrails_max_loops=row.guardrails_max_loops,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def content_item_to_detail(row: ContentItem) -> ContentItemDetail:
    """Convert a ContentItem DB row to a full ContentItemDetail schema."""

    return ContentItemDetail(
        id=row.id,
        author_id=row.author_id,
        source_prompt=row.source_prompt,
        subject=row.subject,
        genre=row.genre,
        age_group=row.age_group,
        video_length_minutes=row.video_length_minutes,
        target_word_count=row.target_word_count,
        title=row.title,
        description=row.description,
        synopsis=row.synopsis,
        story_text=row.story_text,
        status=row.status,
        guardrails_enabled=row.guardrails_enabled,
        guardrails_max_loops=row.guardrails_max_loops,
        created_at=row.created_at,
        updated_at=row.updated_at,
        has_thumbnail=row.thumbnail_blob is not None,
        has_audio=row.audio_blob is not None,
        thumbnail_mime_type=row.thumbnail_mime_type,
        audio_mime_type=row.audio_mime_type,
        audio_voice=row.audio_voice,
        audio_generated_at=row.audio_generated_at,
    )
