from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.auth.password import hash_password
from app.config import Settings
from app.db.base import Base
from app.db.models import (  # noqa: F401 — register models with Base.metadata
    AuditEvent,
    ContentItem,
    GenerationRun,
    GuardrailsEvent,
    ModelCall,
    User,
)


def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    """Enable SQLite foreign-key enforcement on each new connection."""

    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def build_engine(sqlite_path: str):
    """Create a SQLAlchemy engine for the given SQLite database path."""

    engine = create_engine(
        f"sqlite:///{sqlite_path}",
        connect_args={"check_same_thread": False},
    )
    event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


def seed_admin_user(db: Session, settings: Settings) -> None:
    """Create or update the admin user from environment-configured credentials."""

    if not settings.admin_username or not settings.admin_password:
        return
    username = settings.admin_username.strip()
    pwd_hash = hash_password(settings.admin_password)
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        db.add(
            User(
                username=username,
                password_hash=pwd_hash,
                role="admin",
                is_active=True,
                email_verified=True,
            )
        )
    else:
        user.password_hash = pwd_hash
        user.role = "admin"
        user.is_active = True
        user.email_verified = True
    db.commit()


def configure_database(app: FastAPI, settings: Settings) -> None:
    """Initialize the DB engine, run migrations, seed admin, and attach state."""

    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    engine = build_engine(str(settings.sqlite_path))
    Base.metadata.create_all(bind=engine)

    # SQLite create_all() does not add columns to existing DBs. Keep best-effort
    # local compatibility for schema additions used by auth/content flows.
    with engine.begin() as conn:
        cols = conn.execute(text("PRAGMA table_info(content_items)")).fetchall()
        existing = {row[1] for row in cols}
        if "synopsis" not in existing:
            conn.execute(text("ALTER TABLE content_items ADD COLUMN synopsis TEXT"))
        user_cols = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        user_existing = {row[1] for row in user_cols}
        if "email" not in user_existing:
            conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(320)"))
        if "email_verified" not in user_existing:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN email_verified BOOLEAN "
                    "NOT NULL DEFAULT 0"
                )
            )
        if "email_verification_token_hash" not in user_existing:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN email_verification_token_hash "
                    "VARCHAR(128)"
                )
            )
        if "email_verification_sent_at" not in user_existing:
            conn.execute(text("ALTER TABLE users ADD COLUMN email_verification_sent_at DATETIME"))
        if "email_verification_expires_at" not in user_existing:
            conn.execute(
                text("ALTER TABLE users ADD COLUMN email_verification_expires_at DATETIME")
            )
        if "failed_login_count" not in user_existing:
            conn.execute(
                text(
                    "ALTER TABLE users ADD COLUMN failed_login_count INTEGER "
                    "NOT NULL DEFAULT 0"
                )
            )
        if "locked_until" not in user_existing:
            conn.execute(text("ALTER TABLE users ADD COLUMN locked_until DATETIME"))

    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
    with SessionLocal() as db:
        seed_admin_user(db, settings)
    app.state.settings = settings
    app.state.engine = engine
    app.state.SessionLocal = SessionLocal
