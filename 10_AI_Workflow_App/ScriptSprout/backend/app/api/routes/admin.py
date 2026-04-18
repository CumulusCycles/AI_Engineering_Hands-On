from __future__ import annotations

import shutil
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.query_params import OPTIONAL_STATUS_QUERY_DESCRIPTION, normalize_optional_query_str
from app.db.bootstrap import seed_admin_user
from app.db.deps import get_db
from app.db.models import (
    AuditEvent,
    AuthSession,
    ContentItem,
    GenerationRun,
    GuardrailsEvent,
    ModelCall,
    User,
)
from app.db.repos.admin_metrics import compute_admin_metrics, resolve_metrics_window
from app.db.repos.content_items import (
    count_all_content_items,
    get_content_item_by_id,
    list_all_content_with_author_usernames,
)
from app.schemas.admin import AdminCleanseRequest, AdminCleanseResponse, AdminPingResponse
from app.schemas.admin_content import (
    AdminContentItemDetail,
    AdminContentListPage,
    content_item_to_admin_detail,
    row_tuple_to_admin_list_item,
)
from app.schemas.admin_generation_runs import (
    AdminGenerationRunDetail,
    generation_run_to_admin_detail,
)
from app.schemas.admin_metrics import AdminMetricsResponse
from app.services.chroma_store import rebind_app_chroma_after_disk_wipe

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/ping", response_model=AdminPingResponse)
def admin_ping(_user: Annotated[User, Depends(require_admin)]) -> AdminPingResponse:
    """Handle an admin-scoped operation for this route.

    Args:
        _user: Authenticated user dependency used for access control.

    Returns:
        Result generated for the caller.

    """

    return AdminPingResponse()


@router.get("/metrics", response_model=AdminMetricsResponse)
def admin_get_metrics(
    _user: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
    start: Annotated[
        datetime | None,
        Query(
            description=(
                "Inclusive window start (ISO 8601, UTC recommended). "
                "When omitted with ``end``, defaults to ``end`` minus 7 days."
            ),
        ),
    ] = None,
    end: Annotated[
        datetime | None,
        Query(
            description=(
                "Inclusive window end (ISO 8601). When omitted, defaults to now (UTC). "
                "When both bounds are omitted, the window is the last 7 days ending now."
            ),
        ),
    ] = None,
) -> AdminMetricsResponse:
    """Handle an admin-scoped operation for this route.

    Args:
        _user: Authenticated user dependency used for access control.
        db: Active database session for repository operations.
        start: Inclusive start timestamp for time-window filtering.
        end: Inclusive end timestamp for time-window filtering.

    Returns:
        Result generated for the caller.

    """

    try:
        start_u, end_u, used_default = resolve_metrics_window(start, end)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return compute_admin_metrics(db, start_u, end_u, used_default_window=used_default)


@router.get("/content/", response_model=AdminContentListPage)
def admin_list_content(
    _user: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    content_status: Annotated[
        str | None,
        Query(alias="status", max_length=64, description=OPTIONAL_STATUS_QUERY_DESCRIPTION),
    ] = None,
    author_id: Annotated[int | None, Query(ge=1)] = None,
) -> AdminContentListPage:
    """Handle an admin-scoped operation for this route.

    Args:
        _user: Authenticated user dependency used for access control.
        db: Active database session for repository operations.
        limit: Input value used to perform this operation.
        offset: Input value used to perform this operation.
        content_status: Input value used to perform this operation.
        author_id: Unique identifier for the target resource.

    Returns:
        Result generated for the caller.

    """

    status_filter = normalize_optional_query_str(content_status)
    total = count_all_content_items(db, status=status_filter, author_id=author_id)
    pairs = list_all_content_with_author_usernames(
        db,
        limit=limit,
        offset=offset,
        status=status_filter,
        author_id=author_id,
    )
    return AdminContentListPage(
        items=[row_tuple_to_admin_list_item(r, u) for r, u in pairs],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/content/{content_id}", response_model=AdminContentItemDetail)
def admin_get_content(
    content_id: int,
    _user: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
) -> AdminContentItemDetail:
    """Handle an admin-scoped operation for this route.

    Args:
        content_id: Target content identifier.
        _user: Authenticated user dependency used for access control.
        db: Active database session for repository operations.

    Returns:
        Result generated for the caller.

    """

    row = get_content_item_by_id(db, content_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content not found")
    author = db.get(User, row.author_id)
    username = author.username if author is not None else "?"
    return content_item_to_admin_detail(row, username)


@router.post("/cleanse", response_model=AdminCleanseResponse)
def admin_cleanse_db_and_vectorstore(
    body: AdminCleanseRequest,
    _user: Annotated[User, Depends(require_admin)],
    request: Request,
    db: Session = Depends(get_db),
) -> AdminCleanseResponse:
    """Handle an admin-scoped operation for this route.

    Args:
        body: Validated request payload.
        _user: Authenticated user dependency used for access control.
        request: Incoming HTTP request context.
        db: Active database session for repository operations.

    Returns:
        Result generated for the caller.

    """

    if not body.confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="confirm=true required")

    settings = request.app.state.settings
    if not settings.allow_admin_cleanse:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin cleanse is disabled. Set ALLOW_ADMIN_CLEANSE=true to enable.",
        )

    if not settings.admin_username or not settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ADMIN_USERNAME and ADMIN_PASSWORD must be set to reseed admin user",
        )

    cleared: dict[str, int] = {}

    # Delete dependent rows explicitly to keep SQLite happy even without relying on cascade order.
    for model in (
        AuthSession,
        ModelCall,
        GuardrailsEvent,
        GenerationRun,
        AuditEvent,
        ContentItem,
        User,
    ):
        result = db.execute(delete(model))
        cleared[model.__tablename__] = int(result.rowcount or 0)

    db.commit()

    chroma_wiped = False
    chroma_path = settings.chroma_path
    try:
        if chroma_path.exists():
            shutil.rmtree(chroma_path)
        chroma_path.mkdir(parents=True, exist_ok=True)
        chroma_wiped = True
    except OSError:
        # Wiping the vectorstore isn't critical for DB integrity, but still surface an error.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to wipe Chroma",
        )

    try:
        rebind_app_chroma_after_disk_wipe(request.app, settings)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chroma path was reset but reopening the vector store failed; restart the API.",
        ) from exc

    # Reseed admin from env (Option B).
    seed_admin_user(db, settings)
    db.commit()

    return AdminCleanseResponse(
        reseeded_admin=True,
        cleared=cleared,
        chroma_wiped=chroma_wiped,
    )


@router.get("/generation-runs/{run_id}", response_model=AdminGenerationRunDetail)
def admin_get_generation_run(
    run_id: int,
    _user: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
) -> AdminGenerationRunDetail:
    """Handle an admin-scoped operation for this route.

    Args:
        run_id: Unique identifier for the target resource.
        _user: Authenticated user dependency used for access control.
        db: Active database session for repository operations.

    Returns:
        Result generated for the caller.

    """

    row = db.get(GenerationRun, run_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generation run not found",
        )

    # Relationship lazy-loads within request scope.
    return generation_run_to_admin_detail(row)
