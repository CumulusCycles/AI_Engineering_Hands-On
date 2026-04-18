"""audit_events repository helpers (transaction staging + SQL count)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.auth.password import hash_password
from app.db.models import AuditEvent, User
from app.db.repos.audit_events import count_audit_events, insert_audit_event


def test_count_audit_events_uses_scalar_query(tmp_path, monkeypatch) -> None:
    """count_audit_events should not load full row lists."""

    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "audit_count.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma"))
    monkeypatch.setenv("EXPOSE_META_WITHOUT_AUTH", "true")
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application):
        SessionLocal = application.state.SessionLocal
        with SessionLocal() as db:
            user = User(
                username="audit_counter",
                password_hash=hash_password("Password123"),
                role="author",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            insert_audit_event(
                db,
                user_id=user.id,
                event_type="evt_a",
                entity_type="content_item",
                entity_id=1,
                payload=None,
            )
            db.commit()
            insert_audit_event(
                db,
                user_id=user.id,
                event_type="evt_b",
                entity_type="content_item",
                entity_id=2,
                payload=None,
            )
            db.commit()
            uid = user.id

        with SessionLocal() as db:
            assert count_audit_events(db) == 2
            assert count_audit_events(db, user_id=uid) == 2
            assert count_audit_events(db, event_type="evt_a") == 1
            raw = int(db.scalar(select(func.count()).select_from(AuditEvent)) or 0)
            assert raw == 2

    get_settings.cache_clear()


def test_insert_audit_event_does_not_commit_alone(tmp_path, monkeypatch) -> None:
    """Caller must commit; uncommitted audit rows are not visible in a new session."""

    monkeypatch.setenv("SQLITE_PATH", str(tmp_path / "audit_tx.db"))
    monkeypatch.setenv("CHROMA_PATH", str(tmp_path / "chroma2"))
    monkeypatch.setenv("EXPOSE_META_WITHOUT_AUTH", "true")
    monkeypatch.delenv("ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    from app.config import get_settings

    get_settings.cache_clear()
    from app.main import create_app

    application = create_app()
    with TestClient(application):
        SessionLocal = application.state.SessionLocal
        with SessionLocal() as db:
            user = User(
                username="audit_tx_user",
                password_hash=hash_password("Password123"),
                role="author",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            insert_audit_event(
                db,
                user_id=user.id,
                event_type="pending_evt",
                entity_type="content_item",
                entity_id=99,
                payload=None,
            )

        with SessionLocal() as db2:
            n = int(db2.scalar(select(func.count()).select_from(AuditEvent)) or 0)
            assert n == 0

    get_settings.cache_clear()
