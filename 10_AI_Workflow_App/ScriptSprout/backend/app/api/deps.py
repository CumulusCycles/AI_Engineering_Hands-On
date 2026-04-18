from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.db.models import AuthSession, ContentItem, User
from app.db.repos.content_items import get_content_item_by_id


def _as_utc_aware(dt: datetime) -> datetime:
    """Ensure a datetime is UTC-aware, attaching UTC tzinfo if naive."""

    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Validate the session cookie and return the authenticated User, or raise 401."""

    settings = request.app.state.settings
    raw = request.cookies.get(settings.session_cookie_name)
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    row = db.scalar(select(AuthSession).where(AuthSession.id == raw))
    if row is None or row.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    now = datetime.now(UTC)
    if _as_utc_aware(row.expires_at) <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    user = db.get(User, row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user


def require_roles(*allowed_roles: str) -> Callable[..., User]:
    """Return a FastAPI dependency that restricts access to the given roles."""

    allowed = frozenset(allowed_roles)

    def _require(user: User = Depends(get_current_user)) -> User:
        """Raise 403 if the authenticated user's role is not in the allowed set."""

        if user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return _require


# Common role dependencies
require_admin = require_roles("admin")
require_author = require_roles("author")


def get_owned_content_or_404(
    content_id: int,
    user: Annotated[User, Depends(require_author)],
    db: Session = Depends(get_db),
) -> ContentItem:
    """Load a ContentItem by ID and verify the current author owns it, or raise 404."""

    row = get_content_item_by_id(db, content_id)
    if row is None or row.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found",
        )
    return row
