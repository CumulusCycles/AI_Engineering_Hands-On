from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import func, select

from app.config import Settings
from app.db.models import User
from app.schemas.meta import ChromaStatusResponse, DbStatusResponse

router = APIRouter(prefix="/api/meta", tags=["meta"])


def _ensure_meta_public_or_404(settings: Settings) -> None:
    """Raise 404 when EXPOSE_META_WITHOUT_AUTH is disabled."""

    if not settings.expose_meta_without_auth:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        )


@router.get(
    "/db-status",
    response_model=DbStatusResponse,
    summary="Database bootstrap status",
    description=(
        "Reports whether SQLite is reachable and whether any users exist (no totals or admin-env "
        "hints). Returns **404** unless **`EXPOSE_META_WITHOUT_AUTH=true`**. "
        "When enabled: still unauthenticated — do not expose on the public internet."
    ),
)
def get_db_status(request: Request) -> DbStatusResponse:
    """Check SQLite reachability and whether any users exist."""

    settings = request.app.state.settings
    _ensure_meta_public_or_404(settings)
    SessionLocal = request.app.state.SessionLocal
    with SessionLocal() as db:
        user_count = int(db.scalar(select(func.count(User.id))) or 0)
    return DbStatusResponse(
        database_reachable=True,
        has_users=user_count > 0,
    )


@router.get(
    "/chroma-status",
    response_model=ChromaStatusResponse,
    summary="Chroma persistence and collection status",
    description=(
        "Chroma persist path, collection name, and vector count. "
        "Returns **404** unless **`EXPOSE_META_WITHOUT_AUTH=true`**. "
        "When enabled: unauthenticated — local demos only."
    ),
)
def get_chroma_status(request: Request) -> ChromaStatusResponse:
    """Return Chroma collection name, persist path, and document count."""

    settings = request.app.state.settings
    _ensure_meta_public_or_404(settings)
    collection = request.app.state.chroma_collection
    return ChromaStatusResponse(
        chroma_reachable=True,
        persist_path=str(settings.chroma_path),
        collection_name=collection.name,
        document_count=int(collection.count()),
        planned_embedding_model=settings.openai_embedding_model,
    )
