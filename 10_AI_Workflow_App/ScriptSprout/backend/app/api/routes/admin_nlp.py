"""Admin NLP orchestration: natural-language routing to metrics and semantic search."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.openai_route_errors import (
    OPENAI_ROUTE_SDK_EXCEPTIONS,
    ensure_openai_client,
    http_exception_from_openai_route_error,
)
from app.db.deps import get_db
from app.db.models import User
from app.schemas.admin_nlp_query import AdminNlpQueryRequest, AdminNlpQueryResponse
from app.services.admin_nlp_orchestration import run_admin_nlp_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post(
    "/nlp-query",
    response_model=AdminNlpQueryResponse,
    summary="Admin NLP query (metrics + optional semantic search)",
    description=(
        "Uses OpenAI **`responses.parse`** to route the admin's **``query``** to one or both "
        "tools: SQLite **metrics** (same aggregates as **`GET /api/admin/metrics`**) and/or "
        "**semantic search** over **`content_semantic_index`** (admin-scoped full index). "
        "Requires **`OPENAI_API_KEY`**."
    ),
)
def admin_nlp_query_route(
    body: AdminNlpQueryRequest,
    _user: Annotated[User, Depends(require_admin)],
    request: Request,
    db: Session = Depends(get_db),
) -> AdminNlpQueryResponse:
    """Handle an admin-scoped operation for this route.

    Args:
        body: Validated request payload.
        _user: Authenticated user dependency used for access control.
        request: Incoming HTTP request context.
        db: Active database session for repository operations.

    Returns:
        Result generated for the caller.

    """

    settings = request.app.state.settings
    client = ensure_openai_client(settings)
    collection = request.app.state.chroma_collection

    try:
        return run_admin_nlp_query(
            client=client,
            model=settings.openai_admin_nlp_model,
            user_query=body.query,
            settings=settings,
            db=db,
            user=_user,
            chroma_collection=collection,
            max_attempts=settings.transient_retry_max_attempts,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(
            exc,
            logger=logger,
            log_context="admin_nlp_query",
            runtime_error_detail="Could not complete admin NLP orchestration",
            openai_error_log_message="admin_nlp_query failed",
        ) from exc
