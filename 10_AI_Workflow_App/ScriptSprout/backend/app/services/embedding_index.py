"""Embed title + description + story_text and upsert into Chroma ``content_semantic_index``."""

from __future__ import annotations

from typing import Any

from chromadb.api.models.Collection import Collection
from openai import OpenAI
from sqlalchemy.orm import Session

from app.db.models import ContentItem
from app.db.repos.model_calls import insert_model_call
from app.services.openai_retry import call_with_transient_retry


def build_semantic_index_document(content: ContentItem) -> str:
    """Concatenate title, description, and story_text into a single embeddable document."""

    title = (content.title or "").strip()
    description = (content.description or "").strip()
    story = (content.story_text or "").strip()
    return (
        f"Title:\n{title}\n\n"
        f"Description:\n{description}\n\n"
        f"Story:\n{story}"
    )


def _embedding_prompt_tokens(resp: Any) -> int | None:
    """Extract prompt_tokens from an OpenAI embeddings response, if present."""

    u = getattr(resp, "usage", None)
    if u is None:
        return None
    pt = getattr(u, "prompt_tokens", None)
    return pt if isinstance(pt, int) else None


def run_single_text_embedding(
    *,
    client: OpenAI,
    embedding_model: str,
    text: str,
    max_attempts: int,
    db: Session,
    user_id: int,
    purpose: str,
) -> tuple[list[float], int, str]:
    """Embed a single text via OpenAI and return (vector, attempts_used, resolved_model)."""

    def _create():
        """Call OpenAI embeddings.create for the given text."""

        return client.embeddings.create(
            model=embedding_model,
            input=text,
            encoding_format="float",
        )

    def _after_attempt(
        attempt: int,
        latency_ms: float,
        exc: BaseException | None,
        result: Any | None,
    ) -> None:
        """Log a model_call row after each embedding attempt."""

        ok = exc is None and result is not None
        ti: int | None = None
        err: str | None = None
        if ok and result is not None:
            ti = _embedding_prompt_tokens(result)
        if exc is not None:
            err = type(exc).__name__
        resolved_model = embedding_model
        if result is not None:
            resolved_model = getattr(result, "model", None) or embedding_model
        insert_model_call(
            db,
            user_id=user_id,
            operation_type="embeddings_create",
            model_name=str(resolved_model),
            purpose=purpose,
            attempt_index=attempt,
            success=ok,
            latency_ms=max(0, int(round(latency_ms))),
            token_input=ti,
            token_output=None,
            error_type=err,
        )

    resp, attempts_used = call_with_transient_retry(
        _create,
        max_attempts=max_attempts,
        after_attempt=_after_attempt,
    )

    data = getattr(resp, "data", None) or []
    if not data:
        msg = "OpenAI returned no embedding rows"
        raise RuntimeError(msg)
    vector = getattr(data[0], "embedding", None)
    if not vector:
        msg = "OpenAI returned empty embedding vector"
        raise RuntimeError(msg)

    resolved = getattr(resp, "model", None) or embedding_model
    return list(vector), attempts_used, str(resolved)


def run_upsert_semantic_index(
    *,
    client: OpenAI,
    embedding_model: str,
    collection: Collection,
    content: ContentItem,
    max_attempts: int,
    db: Session,
    user_id: int,
) -> tuple[int, str, int]:
    """Embed a ContentItem and upsert it into Chroma; return (attempts, model, doc_count)."""

    doc_text = build_semantic_index_document(content)

    vector, attempts_used, _resolved = run_single_text_embedding(
        client=client,
        embedding_model=embedding_model,
        text=doc_text,
        max_attempts=max_attempts,
        db=db,
        user_id=user_id,
        purpose="semantic_index",
    )

    created = content.created_at
    created_iso = created.isoformat() if created is not None else ""

    meta = {
        "content_id": int(content.id),
        "author_id": int(content.author_id),
        "genre": (content.genre or "").strip(),
        "age_group": (content.age_group or "").strip(),
        "status": str(content.status),
        "created_at": created_iso,
    }

    collection.upsert(
        ids=[str(content.id)],
        embeddings=[vector],
        documents=[doc_text],
        metadatas=[meta],
    )

    doc_count = int(collection.count())
    return attempts_used, _resolved, doc_count
