from pydantic import BaseModel, Field


class ChromaStatusResponse(BaseModel):
    """Chroma persistence + collection readiness for local demos (no secrets)."""

    chroma_reachable: bool = Field(
        description="True when the persistent client and collection are usable",
    )
    persist_path: str = Field(description="Configured CHROMA_PATH directory")
    collection_name: str = Field(description="Vector collection for semantic content search")
    document_count: int = Field(
        description=(
            "Rows in content_semantic_index; increments when authors POST …/semantic-index"
        ),
        ge=0,
    )
    planned_embedding_model: str = Field(
        description=(
            "Configured OpenAI embedding model (OPENAI_EMBEDDING_MODEL; POST …/semantic-index)"
        ),
    )


class DbStatusResponse(BaseModel):
    """Lightweight DB bootstrap status for demos (no counts, no admin-env hints).

    Intentionally coarse so enabling ``EXPOSE_META_WITHOUT_AUTH`` on a reachable host does not
    leak user totals, admin headcount, or whether bootstrap credentials exist in the environment.
    """

    database_reachable: bool = Field(description="True when SQLite is initialized")
    has_users: bool = Field(
        description="True when at least one row exists in the users table",
    )
