from pydantic import BaseModel, Field


class UpsertSemanticIndexResponse(BaseModel):
    """Result of embedding title+description+story and upserting into Chroma."""

    content_id: int = Field(
        description="SQLite content_items.id; same logical id as the Chroma document",
    )
    embedding_model: str = Field(description="OpenAI embedding model used for this vector")
    chroma_document_id: str = Field(
        description="Chroma upsert id (string form of content_id)",
    )
    attempts_used: int = Field(
        ge=1,
        description="Embedding API attempts, including transient retries",
    )
    collection_document_count: int = Field(
        ge=0,
        description="Rows in content_semantic_index after this upsert",
    )
