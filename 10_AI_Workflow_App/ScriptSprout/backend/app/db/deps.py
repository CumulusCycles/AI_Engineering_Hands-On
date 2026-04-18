from __future__ import annotations

from collections.abc import Generator

from fastapi import Request
from sqlalchemy.orm import Session


def get_db(request: Request) -> Generator[Session, None, None]:
    """Retrieve data needed for this operation.

    Args:
        request: Incoming HTTP request context.

    Returns:
        Result generated for the caller.

    """

    SessionLocal = request.app.state.SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
