from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.content import ContentListItem


class SemanticSearchRequest(BaseModel):
    """Natural-language query embedding against ``content_semantic_index``."""

    query: str = Field(
        min_length=1,
        max_length=16_000,
        description="Search text; embedded with the same model as indexing.",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum hits to return (Chroma nearest neighbors, then SQLite hydration).",
    )
    genre: str | None = Field(
        default=None,
        max_length=128,
        description="Optional Chroma metadata filter; must match indexed ``genre`` exactly.",
    )
    status: str | None = Field(
        default=None,
        max_length=64,
        description="Optional Chroma metadata filter; must match indexed ``status`` exactly.",
    )


class SemanticSearchHit(BaseModel):
    """One ranked row: Chroma distance (lower is closer) plus list-shaped content."""

    distance: float = Field(description="Chroma distance for this hit; lower is more similar.")
    content: ContentListItem


class SemanticSearchResponse(BaseModel):
    items: list[SemanticSearchHit]
    embedding_model: str
    attempts_used: int = Field(ge=0, description="Embedding API attempts for the query vector.")
