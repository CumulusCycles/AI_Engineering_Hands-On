"""Semantic search: Chroma nearest neighbors, SQLite hydration, role-scoped metadata filters."""

from __future__ import annotations

from dataclasses import dataclass

from chromadb.api.models.Collection import Collection
from openai import OpenAI
from sqlalchemy.orm import Session

from app.api.query_params import normalize_optional_query_str
from app.db.models import User
from app.db.repos.content_items import get_content_items_by_ids
from app.schemas.content import ContentListItem, content_item_to_list_item
from app.services.embedding_index import run_single_text_embedding


def build_chroma_where(
    *,
    user_role: str,
    user_id: int,
    genre: str | None,
    status: str | None,
) -> dict | None:
    """Build and return a derived value for downstream use.

    Args:
        user_role: Input value used to perform this operation.
        user_id: Unique identifier for the target resource.
        genre: Input value used to perform this operation.
        status: Input value used to perform this operation.

    Returns:
        Result generated for the caller.

    """

    conditions: list[dict] = []
    if user_role == "author":
        conditions.append({"author_id": int(user_id)})
    g = normalize_optional_query_str(genre)
    if g is not None:
        conditions.append({"genre": g})
    s = normalize_optional_query_str(status)
    if s is not None:
        conditions.append({"status": s})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


@dataclass(frozen=True, slots=True)
class SemanticSearchHitInternal:
    distance: float
    content: ContentListItem


def run_semantic_search(
    *,
    client: OpenAI,
    embedding_model: str,
    collection: Collection,
    query_text: str,
    limit: int,
    db: Session,
    user: User,
    max_attempts: int,
    genre: str | None,
    status: str | None,
) -> tuple[list[SemanticSearchHitInternal], int, str]:
    """Execute the workflow and return its result.

    Args:
        client: Input value used to perform this operation.
        embedding_model: Input value used to perform this operation.
        collection: Input value used to perform this operation.
        query_text: Input value used to perform this operation.
        limit: Input value used to perform this operation.
        db: Active database session for repository operations.
        user: Authenticated user for authorization and ownership checks.
        max_attempts: Input value used to perform this operation.
        genre: Input value used to perform this operation.
        status: Input value used to perform this operation.

    Returns:
        Result generated for the caller.

    """

    vector, attempts_used, model_used = run_single_text_embedding(
        client=client,
        embedding_model=embedding_model,
        text=query_text,
        max_attempts=max_attempts,
        db=db,
        user_id=user.id,
        purpose="semantic_search",
    )

    where = build_chroma_where(
        user_role=user.role,
        user_id=user.id,
        genre=genre,
        status=status,
    )

    raw = collection.query(
        query_embeddings=[vector],
        n_results=limit,
        where=where,
        include=["distances"],
    )

    id_lists = raw.get("ids") or []
    dist_lists = raw.get("distances") or []
    if not id_lists or not id_lists[0]:
        return [], attempts_used, model_used

    chroma_ids = id_lists[0]
    distances = dist_lists[0] if dist_lists and dist_lists[0] is not None else []

    # Parse valid integer IDs and batch-load from DB in a single query.
    parsed_ids: list[tuple[int, int]] = []  # (idx, content_id)
    for idx, cid in enumerate(chroma_ids):
        try:
            parsed_ids.append((idx, int(cid)))
        except (TypeError, ValueError):
            continue

    rows_by_id = get_content_items_by_ids(db, [cid for _, cid in parsed_ids])

    hits: list[SemanticSearchHitInternal] = []
    for idx, content_id in parsed_ids:
        row = rows_by_id.get(content_id)
        if row is None:
            continue
        if user.role == "author" and row.author_id != user.id:
            continue
        dist = float(distances[idx]) if idx < len(distances) else 0.0
        hits.append(
            SemanticSearchHitInternal(
                distance=dist,
                content=content_item_to_list_item(row),
            ),
        )

    return hits, attempts_used, model_used
