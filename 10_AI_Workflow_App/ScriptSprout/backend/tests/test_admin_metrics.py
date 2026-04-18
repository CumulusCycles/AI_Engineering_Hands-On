"""Admin metrics aggregation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.models import AuditEvent, ContentItem, User


def _login_admin(c: TestClient) -> None:
    r = c.post(
        "/api/auth/login",
        json={"username": "seedadmin", "password": "seedpassword123"},
    )
    assert r.status_code == 200


def test_admin_metrics_requires_auth(client: TestClient) -> None:
    r = client.get("/api/admin/metrics")
    assert r.status_code == 401


def test_admin_metrics_author_forbidden(client: TestClient) -> None:
    client.post(
        "/api/auth/register",
        json={"username": "metrics_author", "password": "Password123"},
    )
    client.post(
        "/api/auth/login",
        json={"username": "metrics_author", "password": "Password123"},
    )
    r = client.get("/api/admin/metrics")
    assert r.status_code == 403


def test_admin_metrics_empty_window(client_with_admin: TestClient) -> None:
    _login_admin(client_with_admin)
    r = client_with_admin.get("/api/admin/metrics")
    assert r.status_code == 200
    body = r.json()
    assert body["window"]["used_default_window"] is True
    assert "start" in body["window"]
    assert "end" in body["window"]
    assert body["content"]["items_created"] == 0
    assert body["model_calls"]["total"] == 0
    assert body["generation_runs"]["total"] == 0
    assert body["guardrails"]["events_total"] == 0
    assert body["audit"]["events_total"] == 0


def test_admin_metrics_invalid_range(client_with_admin: TestClient) -> None:
    _login_admin(client_with_admin)
    r = client_with_admin.get(
        "/api/admin/metrics",
        params={
            "start": "2025-01-10T00:00:00Z",
            "end": "2025-01-01T00:00:00Z",
        },
    )
    assert r.status_code == 422


def test_admin_metrics_span_too_large(client_with_admin: TestClient) -> None:
    _login_admin(client_with_admin)
    r = client_with_admin.get(
        "/api/admin/metrics",
        params={
            "start": "2020-01-01T00:00:00Z",
            "end": "2025-12-31T23:59:59Z",
        },
    )
    assert r.status_code == 422
    assert "366" in r.json()["detail"]


def test_admin_metrics_counts_seed_rows(
    tmp_path,
    monkeypatch,
) -> None:
    """Seed ORM rows and assert aggregates for an explicit UTC window."""

    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "metrics.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma_m"))
    monkeypatch.setenv("EXPOSE_META_WITHOUT_AUTH", "true")
    monkeypatch.setenv("ADMIN_USERNAME", "seedadmin")
    monkeypatch.setenv("ADMIN_PASSWORD", "seedpassword123")

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    start = datetime(2025, 3, 1, 12, 0, 0, tzinfo=UTC)
    end = datetime(2025, 3, 1, 18, 0, 0, tzinfo=UTC)

    with TestClient(application) as c:
        SessionLocal = application.state.SessionLocal
        with SessionLocal() as db:
            author = db.scalar(select(User).where(User.username == "seedadmin"))
            assert author is not None
            item = ContentItem(
                author_id=author.id,
                source_prompt="p",
                status="draft",
                genre="fantasy",
            )
            item.created_at = start
            db.add(item)
            db.flush()
            db.add(
                AuditEvent(
                    user_id=author.id,
                    event_type="step_approved",
                    entity_type="content_item",
                    entity_id=item.id,
                    created_at=start,
                )
            )
            db.commit()

        _login_admin(c)
        r = c.get(
            "/api/admin/metrics",
            params={
                "start": start.isoformat(),
                "end": end.isoformat(),
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["window"]["used_default_window"] is False
        assert body["content"]["items_created"] == 1
        genres = {b["label"]: b["count"] for b in body["content"]["by_genre"]}
        assert genres.get("fantasy") == 1
        assert body["audit"]["events_total"] == 1
        types = {b["label"]: b["count"] for b in body["audit"]["by_event_type"]}
        assert types.get("step_approved") == 1

    get_settings.cache_clear()


def test_admin_metrics_excludes_outside_window(
    tmp_path,
    monkeypatch,
) -> None:
    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "metrics2.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma_m2"))
    monkeypatch.setenv("EXPOSE_META_WITHOUT_AUTH", "true")
    monkeypatch.setenv("ADMIN_USERNAME", "seedadmin")
    monkeypatch.setenv("ADMIN_PASSWORD", "seedpassword123")

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    old = datetime(2020, 1, 1, tzinfo=UTC)
    window_start = datetime.now(tz=UTC) - timedelta(days=1)
    window_end = datetime.now(tz=UTC)

    with TestClient(application) as c:
        SessionLocal = application.state.SessionLocal
        with SessionLocal() as db:
            author = db.scalar(select(User).where(User.username == "seedadmin"))
            assert author is not None
            item = ContentItem(author_id=author.id, source_prompt="old", status="draft")
            item.created_at = old
            db.add(item)
            db.commit()

        _login_admin(c)
        r = c.get(
            "/api/admin/metrics",
            params={"start": window_start.isoformat(), "end": window_end.isoformat()},
        )
        assert r.status_code == 200
        assert r.json()["content"]["items_created"] == 0

    get_settings.cache_clear()
