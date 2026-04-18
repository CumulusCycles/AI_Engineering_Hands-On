"""Semantic index: OpenAI embeddings + Chroma upsert + audit_events + model_calls."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models import AuditEvent, ContentItem, ModelCall


def _register_login_author(ac: TestClient, username: str, password: str) -> None:
    r = ac.post("/api/auth/register", json={"username": username, "password": password})
    assert r.status_code == 201
    r2 = ac.post("/api/auth/login", json={"username": username, "password": password})
    assert r2.status_code == 200


def test_semantic_index_upsert_chroma_and_audit(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-dummy-key-for-pytest")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()

    with TestClient(application) as ac:
        _register_login_author(ac, "semantic_author", "Password123")
        create = ac.post(
            "/api/content/",
            json={
                "prompt": "A lighthouse keeper finds a message in a bottle.",
                "genre": "sci-fi",
                "title": "Tide and Signal",
                "description": "A quiet coastal mystery about isolation and discovery.",
                "story_text": (
                    "The light swept the channel. She opened the bottle and read one word: Wait."
                ),
            },
        )
        assert create.status_code == 201
        content_id = create.json()["id"]

        fake_emb = MagicMock()
        fake_emb.model = "text-embedding-3-small"
        fake_emb.data = [MagicMock(embedding=[0.01, 0.02, -0.03])]
        fake_emb.usage = MagicMock(prompt_tokens=12, total_tokens=12)

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.embeddings.create.return_value = fake_emb
            mock_cls.return_value = instance
            r = ac.post(f"/api/content/{content_id}/semantic-index")

    get_settings.cache_clear()

    assert r.status_code == 200
    body = r.json()
    assert body["content_id"] == content_id
    assert body["chroma_document_id"] == str(content_id)
    assert body["embedding_model"] == "text-embedding-3-small"
    assert body["attempts_used"] == 1
    assert body["collection_document_count"] == 1

    chroma_col = application.state.chroma_collection
    got = chroma_col.get(ids=[str(content_id)], include=["embeddings", "documents", "metadatas"])
    assert got["ids"] == [str(content_id)]
    assert got["documents"] and "Tide and Signal" in (got["documents"][0] or "")
    meta = got["metadatas"][0] if got["metadatas"] else {}
    assert meta.get("content_id") == content_id
    assert meta.get("genre") == "sci-fi"

    SessionLocal = application.state.SessionLocal
    with SessionLocal() as db:
        evt = db.scalar(
            select(AuditEvent.id).where(
                (AuditEvent.user_id == db.get(ContentItem, content_id).author_id)
                & (AuditEvent.event_type == "upsert_semantic_index")
                & (AuditEvent.entity_id == content_id),
            )
        )
        assert evt is not None

        mc = db.scalar(
            select(ModelCall.id).where(
                (ModelCall.user_id == db.get(ContentItem, content_id).author_id)
                & (ModelCall.operation_type == "embeddings_create")
                & (ModelCall.purpose == "semantic_index")
                & (ModelCall.success.is_(True)),
            )
        )
        assert mc is not None


def test_semantic_index_requires_fields(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "a.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma_a"))
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    with TestClient(create_app()) as ac:
        _register_login_author(ac, "partial_author", "Password123")
        create = ac.post("/api/content/", json={"prompt": "No story yet"})
        assert create.status_code == 201
        cid = create.json()["id"]
        r = ac.post(f"/api/content/{cid}/semantic-index")
    get_settings.cache_clear()
    assert r.status_code == 400
    detail = r.json().get("detail", "")
    assert "required to build the semantic index document" in detail


def test_semantic_index_openai_key_missing_returns_503(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "b.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma_b"))
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    with TestClient(create_app()) as ac:
        _register_login_author(ac, "no_key_author", "Password123")
        create = ac.post(
            "/api/content/",
            json={
                "prompt": "x",
                "title": "T",
                "description": "D",
                "story_text": "S",
            },
        )
        assert create.status_code == 201
        cid = create.json()["id"]
        r = ac.post(f"/api/content/{cid}/semantic-index")
    get_settings.cache_clear()
    assert r.status_code == 503
