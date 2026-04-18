from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import ContentItem, User


def create_content_item(
    db: Session,
    *,
    author_id: int,
    source_prompt: str,
    subject: str | None = None,
    genre: str | None = None,
    age_group: str | None = None,
    video_length_minutes: int | None = None,
    target_word_count: int | None = None,
    title: str | None = None,
    description: str | None = None,
    story_text: str | None = None,
    guardrails_enabled: bool = True,
    guardrails_max_loops: int = 3,
) -> ContentItem:
    """Insert a new ContentItem in draft status and return the persisted row."""

    row = ContentItem(
        author_id=author_id,
        source_prompt=source_prompt,
        subject=subject,
        genre=genre,
        age_group=age_group,
        video_length_minutes=video_length_minutes,
        target_word_count=target_word_count,
        title=title,
        description=description,
        story_text=story_text,
        status="draft",
        guardrails_enabled=guardrails_enabled,
        guardrails_max_loops=guardrails_max_loops,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_content_item_by_id(db: Session, content_id: int) -> ContentItem | None:
    """Fetch a single ContentItem by primary key, or None if not found."""

    return db.get(ContentItem, content_id)


def get_content_items_by_ids(db: Session, content_ids: list[int]) -> dict[int, ContentItem]:
    """Batch-fetch content items by ID, returning a dict keyed by content_id."""
    if not content_ids:
        return {}
    rows = db.scalars(
        select(ContentItem).where(ContentItem.id.in_(content_ids))
    ).all()
    return {row.id: row for row in rows}


def count_content_items_for_author(
    db: Session,
    author_id: int,
    *,
    status: str | None = None,
) -> int:
    """Count content items owned by an author, optionally filtered by status."""

    stmt = select(func.count()).select_from(ContentItem).where(ContentItem.author_id == author_id)
    if status is not None and status.strip() != "":
        stmt = stmt.where(ContentItem.status == status.strip())
    return int(db.scalar(stmt) or 0)


def list_content_items_for_author(
    db: Session,
    author_id: int,
    *,
    limit: int = 100,
    offset: int = 0,
    status: str | None = None,
) -> list[ContentItem]:
    """List content items for an author, newest first, with optional status filter."""

    stmt = select(ContentItem).where(ContentItem.author_id == author_id)
    if status is not None and status.strip() != "":
        stmt = stmt.where(ContentItem.status == status.strip())
    stmt = (
        stmt.order_by(ContentItem.created_at.desc()).limit(limit).offset(offset)
    )
    return list(db.scalars(stmt).all())


def count_all_content_items(
    db: Session,
    *,
    status: str | None = None,
    author_id: int | None = None,
) -> int:
    """Count all content items, optionally filtered by status and/or author."""

    stmt = select(func.count()).select_from(ContentItem)
    if status is not None and status.strip() != "":
        stmt = stmt.where(ContentItem.status == status.strip())
    if author_id is not None:
        stmt = stmt.where(ContentItem.author_id == author_id)
    return int(db.scalar(stmt) or 0)


def list_all_content_with_author_usernames(
    db: Session,
    *,
    limit: int = 100,
    offset: int = 0,
    status: str | None = None,
    author_id: int | None = None,
) -> list[tuple[ContentItem, str]]:
    """List content items joined with author usernames for admin views."""

    stmt = select(ContentItem, User.username).join(User, ContentItem.author_id == User.id)
    if status is not None and status.strip() != "":
        stmt = stmt.where(ContentItem.status == status.strip())
    if author_id is not None:
        stmt = stmt.where(ContentItem.author_id == author_id)
    stmt = stmt.order_by(ContentItem.created_at.desc()).limit(limit).offset(offset)
    rows = db.execute(stmt).all()
    return [(row[0], row[1]) for row in rows]
