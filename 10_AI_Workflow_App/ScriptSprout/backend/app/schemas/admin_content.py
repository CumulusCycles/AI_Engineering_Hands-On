from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.db.models import ContentItem
from app.schemas.content import ContentItemDetail, build_prompt_preview, content_item_to_detail


class AdminContentListItem(BaseModel):
    """Cross-author summary for admin browse (read-only)."""

    id: int
    author_id: int
    author_username: str
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


class AdminContentListPage(BaseModel):
    items: list[AdminContentListItem]
    total: int
    limit: int
    offset: int


class AdminContentItemDetail(ContentItemDetail):
    """Full row plus owning author username (admin read-only)."""

    author_username: str


def row_tuple_to_admin_list_item(row: ContentItem, author_username: str) -> AdminContentListItem:
    """Convert a ContentItem and its author username to an admin list summary."""

    return AdminContentListItem(
        id=row.id,
        author_id=row.author_id,
        author_username=author_username,
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


def content_item_to_admin_detail(row: ContentItem, author_username: str) -> AdminContentItemDetail:
    """Convert a ContentItem and its author username to a full admin detail schema."""

    base = content_item_to_detail(row).model_dump()
    return AdminContentItemDetail(**base, author_username=author_username)
