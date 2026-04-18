"""Semantic search: Chroma query + SQLite hydration + author vs admin scope."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient


def _register(ac: TestClient, username: str, password: str) -> None:
    assert (
        ac.post("/api/auth/register", json={"username": username, "password": password}).status_code
        == 201
    )


def test_semantic_search_requires_auth(client: TestClient) -> None:
    r = client.post("/api/search/semantic", json={"query": "hello"})
    assert r.status_code == 401


def test_semantic_search_empty_index_no_key_ok(client: TestClient) -> None:
    _register(client, "empty_search_author", "Password123")
    assert (
        client.post(
            "/api/auth/login", json={"username": "empty_search_author", "password": "Password123"}
        ).status_code
        == 200
    )
    r = client.post("/api/search/semantic", json={"query": "anything"})
    assert r.status_code == 200
    body = r.json()
    assert body["items"] == []
    assert body["attempts_used"] == 0


def test_semantic_search_author_only_sees_own_vectors(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "s.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma_s"))
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application):
        col = application.state.chroma_collection

    with TestClient(application) as ac:
        _register(ac, "author_a", "Password123")
        _register(ac, "author_b", "Password123")
        assert (
            ac.post(
                "/api/auth/login", json={"username": "author_a", "password": "Password123"}
            ).status_code
            == 200
        )
        ca = ac.post(
            "/api/content/",
            json={
                "prompt": "alpha prompt",
                "genre": "g1",
                "title": "Alpha",
                "description": "Desc A",
                "story_text": "Story A",
            },
        ).json()["id"]
        ac.post("/api/auth/logout")
        assert (
            ac.post(
                "/api/auth/login", json={"username": "author_b", "password": "Password123"}
            ).status_code
            == 200
        )
        cb = ac.post(
            "/api/content/",
            json={
                "prompt": "beta prompt",
                "genre": "g2",
                "title": "Beta",
                "description": "Desc B",
                "story_text": "Story B",
            },
        ).json()["id"]

    with application.state.SessionLocal() as db:
        from app.db.models import ContentItem

        aid_a = db.get(ContentItem, ca).author_id
        aid_b = db.get(ContentItem, cb).author_id

    col.upsert(
        ids=[str(ca), str(cb)],
        embeddings=[[1.0, 0.0], [0.0, 1.0]],
        documents=["da", "db"],
        metadatas=[
            {
                "content_id": ca,
                "author_id": int(aid_a),
                "genre": "g1",
                "status": "draft",
                "created_at": "",
            },
            {
                "content_id": cb,
                "author_id": int(aid_b),
                "genre": "g2",
                "status": "draft",
                "created_at": "",
            },
        ],
    )

    with TestClient(application) as ac:
        assert (
            ac.post(
                "/api/auth/login", json={"username": "author_a", "password": "Password123"}
            ).status_code
            == 200
        )

        fake_emb = MagicMock()
        fake_emb.model = "text-embedding-3-small"
        fake_emb.data = [MagicMock(embedding=[1.0, 0.0])]
        fake_emb.usage = MagicMock(prompt_tokens=3, total_tokens=3)

        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.embeddings.create.return_value = fake_emb
            mock_cls.return_value = instance
            r = ac.post("/api/search/semantic", json={"query": "find alpha", "limit": 5})

    get_settings.cache_clear()
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["content"]["id"] == ca
    assert items[0]["content"]["title"] == "Alpha"


def test_semantic_search_admin_sees_all_authors(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "s2.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma_s2"))
    monkeypatch.setenv("ADMIN_USERNAME", "seedadmin")
    monkeypatch.setenv("ADMIN_PASSWORD", "seedpassword123")
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application):
        col = application.state.chroma_collection

    with TestClient(application) as ac:
        _register(ac, "writer_x", "Password123")
        assert (
            ac.post(
                "/api/auth/login", json={"username": "writer_x", "password": "Password123"}
            ).status_code
            == 200
        )
        cx = ac.post(
            "/api/content/",
            json={
                "prompt": "px",
                "title": "X",
                "description": "Dx",
                "story_text": "Sx",
            },
        ).json()["id"]
        ac.post("/api/auth/logout")
        _register(ac, "writer_y", "Password123")
        assert (
            ac.post(
                "/api/auth/login", json={"username": "writer_y", "password": "Password123"}
            ).status_code
            == 200
        )
        cy = ac.post(
            "/api/content/",
            json={
                "prompt": "py",
                "title": "Y",
                "description": "Dy",
                "story_text": "Sy",
            },
        ).json()["id"]

    with application.state.SessionLocal() as db:
        from app.db.models import ContentItem

        ax = db.get(ContentItem, cx).author_id
        ay = db.get(ContentItem, cy).author_id

    col.upsert(
        ids=[str(cx), str(cy)],
        embeddings=[[1.0, 0.0], [0.2, 1.0]],
        documents=["x", "y"],
        metadatas=[
            {
                "content_id": cx,
                "author_id": int(ax),
                "genre": "",
                "status": "draft",
                "created_at": "",
            },
            {
                "content_id": cy,
                "author_id": int(ay),
                "genre": "",
                "status": "draft",
                "created_at": "",
            },
        ],
    )

    with TestClient(application) as ac:
        assert (
            ac.post(
                "/api/auth/login", json={"username": "seedadmin", "password": "seedpassword123"}
            ).status_code
            == 200
        )
        fake_emb = MagicMock()
        fake_emb.model = "text-embedding-3-small"
        fake_emb.data = [MagicMock(embedding=[1.0, 0.0])]
        fake_emb.usage = MagicMock(prompt_tokens=2, total_tokens=2)
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.embeddings.create.return_value = fake_emb
            mock_cls.return_value = instance
            r = ac.post("/api/search/semantic", json={"query": "nearer to x", "limit": 10})

    get_settings.cache_clear()
    assert r.status_code == 200
    ids = {h["content"]["id"] for h in r.json()["items"]}
    assert ids == {cx, cy}


def test_semantic_search_genre_filter(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "s3.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma_s3"))
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application):
        col = application.state.chroma_collection

    with TestClient(application) as ac:
        _register(ac, "genre_author", "Password123")
        assert (
            ac.post(
                "/api/auth/login", json={"username": "genre_author", "password": "Password123"}
            ).status_code
            == 200
        )
        c_mys = ac.post(
            "/api/content/",
            json={
                "prompt": "p",
                "genre": "mystery",
                "title": "M",
                "description": "D",
                "story_text": "S",
            },
        ).json()["id"]
        c_sf = ac.post(
            "/api/content/",
            json={
                "prompt": "p2",
                "genre": "sci-fi",
                "title": "SF",
                "description": "D2",
                "story_text": "S2",
            },
        ).json()["id"]

    with application.state.SessionLocal() as db:
        from app.db.models import ContentItem

        aid = db.get(ContentItem, c_mys).author_id

    col.upsert(
        ids=[str(c_mys), str(c_sf)],
        embeddings=[[0.0, 1.0], [1.0, 0.0]],
        documents=["a", "b"],
        metadatas=[
            {
                "content_id": c_mys,
                "author_id": aid,
                "genre": "mystery",
                "status": "draft",
                "created_at": "",
            },
            {
                "content_id": c_sf,
                "author_id": aid,
                "genre": "sci-fi",
                "status": "draft",
                "created_at": "",
            },
        ],
    )

    with TestClient(application) as ac:
        assert (
            ac.post(
                "/api/auth/login", json={"username": "genre_author", "password": "Password123"}
            ).status_code
            == 200
        )
        fake_emb = MagicMock()
        fake_emb.model = "text-embedding-3-small"
        fake_emb.data = [MagicMock(embedding=[1.0, 0.0])]
        fake_emb.usage = MagicMock(prompt_tokens=1, total_tokens=1)
        with patch("app.services.openai_client.OpenAI") as mock_cls:
            instance = MagicMock()
            instance.embeddings.create.return_value = fake_emb
            mock_cls.return_value = instance
            r = ac.post(
                "/api/search/semantic",
                json={"query": "q", "genre": "mystery", "limit": 5},
            )

    get_settings.cache_clear()
    assert r.status_code == 200
    assert len(r.json()["items"]) == 1
    assert r.json()["items"][0]["content"]["id"] == c_mys
