"""Admin destructive DB + vectorstore reset (Option B)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.db.models import AuditEvent, AuthSession, ContentItem, ModelCall, User


def test_admin_cleanse_disabled_returns_403(client_with_admin: TestClient) -> None:
    """Destructive reset stays off unless ALLOW_ADMIN_CLEANSE=true."""

    assert (
        client_with_admin.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        ).status_code
        == 200
    )
    r = client_with_admin.post("/api/admin/cleanse", json={"confirm": True})
    assert r.status_code == 403
    body = r.json()
    assert body["code"] == "http_403"
    assert "ALLOW_ADMIN_CLEANSE" in body["detail"]


def test_admin_cleanse_option_b_resets_db_and_chroma(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "test.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("ADMIN_USERNAME", "seedadmin")
    monkeypatch.setenv("ADMIN_PASSWORD", "seedpassword123")
    monkeypatch.setenv("ALLOW_ADMIN_CLEANSE", "true")

    # Build app with isolated settings.
    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    chroma_path = tmp_path / "chroma"

    with TestClient(application) as client:
        # Lifespan has run; settings + SessionLocal are now available.
        SessionLocal = application.state.SessionLocal
        chroma_path = application.state.settings.chroma_path
        chroma_path.mkdir(parents=True, exist_ok=True)
        dummy = chroma_path / "dummy.txt"
        dummy.write_text("x", encoding="utf-8")
        assert any(chroma_path.iterdir())

        # Create an author + some rows so we can verify they are wiped.
        assert (
            client.post(
                "/api/auth/register",
                json={"username": "writer_one", "password": "Password123"},
            ).status_code
            == 201
        )
        assert (
            client.post(
                "/api/auth/login",
                json={"username": "writer_one", "password": "Password123"},
            ).status_code
            == 200
        )
        content_resp = client.post(
            "/api/content/",
            json={"prompt": "admin cleanse should wipe this content", "genre": "mystery"},
        )
        assert content_resp.status_code == 201

        # Login admin and call cleanse.
        client.post("/api/auth/logout")
        r_login_admin = client.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        )
        assert r_login_admin.status_code == 200

        r_bad = client.post("/api/admin/cleanse", json={"confirm": False})
        assert r_bad.status_code == 400

        r = client.post("/api/admin/cleanse", json={"confirm": True})
        assert r.status_code == 200
        body = r.json()
        assert body["reseeded_admin"] is True
        assert body["chroma_wiped"] is True

        # In-process Chroma handles must match the wiped directory (no stale collection).
        assert int(application.state.chroma_collection.count()) == 0

        # Old session was wiped, so the same cookie should no longer authorize.
        r_after = client.get("/api/admin/content/")
        assert r_after.status_code in (401, 403)

        # Login admin again and verify the DB is empty except admin users.
        r_login_admin_2 = client.post(
            "/api/auth/login",
            json={"username": "seedadmin", "password": "seedpassword123"},
        )
        assert r_login_admin_2.status_code == 200

        r_list = client.get("/api/admin/content/")
        assert r_list.status_code == 200
        assert r_list.json()["total"] == 0

    # DB assertions (direct via SQLAlchemy) + Chroma wipe.
    with SessionLocal() as db:
        assert db.scalar(select(func.count(User.id))) == 1  # only reseeded admin
        assert db.scalar(select(func.count(AuthSession.id))) == 1  # admin logged in after cleanse
        assert db.scalar(select(func.count(ContentItem.id))) == 0
        assert db.scalar(select(func.count(ModelCall.id))) == 0
        assert db.scalar(select(func.count(AuditEvent.id))) == 0

    assert chroma_path.exists()
    assert list(chroma_path.iterdir()) == []

