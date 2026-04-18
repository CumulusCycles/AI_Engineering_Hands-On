"""Persistent ChromaDB client and semantic index collection (embeddings in a later milestone)."""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.api.models.Collection import Collection
from fastapi import FastAPI

from app.config import Settings

# One collection for combined title + description + story text embeddings.
CONTENT_SEMANTIC_COLLECTION = "content_semantic_index"


def create_persistent_chroma(
    chroma_path: Path,
    *,
    embedding_model: str,
) -> tuple[chromadb.PersistentClient, Collection]:
    """Open or create a persistent ChromaDB client and the content_semantic_index collection."""

    chroma_path.mkdir(parents=True, exist_ok=True)
    resolved = chroma_path.resolve()
    client = chromadb.PersistentClient(path=str(resolved))
    collection = client.get_or_create_collection(
        name=CONTENT_SEMANTIC_COLLECTION,
        metadata={
            "app": "scriptsprout",
            "index_target": "title_description_story",
            "embedding_model": embedding_model,
        },
    )
    return client, collection


def rebind_app_chroma_after_disk_wipe(app: FastAPI, settings: Settings) -> None:
    """Recreate the ChromaDB client and collection on app.state after a disk wipe."""

    client, collection = create_persistent_chroma(
        settings.chroma_path,
        embedding_model=settings.openai_embedding_model,
    )
    app.state.chroma_client = client
    app.state.chroma_collection = collection
