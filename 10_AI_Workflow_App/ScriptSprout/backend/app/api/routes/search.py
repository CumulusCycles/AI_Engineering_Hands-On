from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.api.openai_route_errors import (
    OPENAI_ROUTE_SDK_EXCEPTIONS,
    ensure_openai_client,
    http_exception_from_openai_route_error,
)
from app.db.deps import get_db
from app.db.models import User
from app.schemas.search import SemanticSearchHit, SemanticSearchRequest, SemanticSearchResponse
from app.services.semantic_search import run_semantic_search

router = APIRouter(prefix="/api/search", tags=["search"])

require_author_or_admin = require_roles("author", "admin")


@router.post(
    "/semantic",
    response_model=SemanticSearchResponse,
    summary="Semantic search over indexed content",
    description=(
        "Embeds ``query`` with the configured OpenAI embedding model, runs Chroma nearest-neighbor "
        "search on ``content_semantic_index``, then hydrates hits from SQLite. "
        "**Authors** only see vectors scoped to ``author_id`` in metadata; **admins** may search "
        "the full index. Optional ``genre`` / ``status`` filters match Chroma metadata from "
        "indexing."
    ),
)
def semantic_search_route(
    body: SemanticSearchRequest,
    user: Annotated[User, Depends(require_author_or_admin)],
    request: Request,
    db: Session = Depends(get_db),
) -> SemanticSearchResponse:
    """Handle the API request and return a typed response.

    Args:
        body: Validated request payload.
        user: Authenticated user for authorization and ownership checks.
        request: Incoming HTTP request context.
        db: Active database session for repository operations.

    Returns:
        Result generated for the caller.

    """

    settings = request.app.state.settings
    collection = request.app.state.chroma_collection

    q = body.query.strip()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Query must not be empty"
        )

    if int(collection.count()) == 0:
        return SemanticSearchResponse(
            items=[],
            embedding_model=settings.openai_embedding_model,
            attempts_used=0,
        )

    client = ensure_openai_client(settings)

    try:
        hits, attempts_used, model_used = run_semantic_search(
            client=client,
            embedding_model=settings.openai_embedding_model,
            collection=collection,
            query_text=q,
            limit=body.limit,
            db=db,
            user=user,
            max_attempts=settings.transient_retry_max_attempts,
            genre=body.genre,
            status=body.status,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(exc) from exc

    return SemanticSearchResponse(
        items=[SemanticSearchHit(distance=h.distance, content=h.content) for h in hits],
        embedding_model=model_used,
        attempts_used=attempts_used,
    )
