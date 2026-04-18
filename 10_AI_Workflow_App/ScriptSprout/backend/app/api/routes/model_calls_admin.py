from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.deps import get_db
from app.db.models import User
from app.db.repos.model_calls import list_model_calls
from app.schemas.model_calls import ModelCallListPage, model_call_to_list_item

router = APIRouter(prefix="/api/admin/model-calls", tags=["admin"])


@router.get(
    "/",
    response_model=ModelCallListPage,
    summary="List model call events (admin)",
    description=(
        "Read-only paginated list of **`model_calls`** rows (newest `id` first). "
        "Used to verify OpenAI attempt logging after **`POST /api/admin/openai/smoke`**."
    ),
)
def admin_list_model_calls(
    _user: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ModelCallListPage:
    """Handle an admin-scoped operation for this route.

    Args:
        _user: Authenticated user dependency used for access control.
        db: Active database session for repository operations.
        limit: Input value used to perform this operation.
        offset: Input value used to perform this operation.

    Returns:
        Result generated for the caller.

    """

    rows, total = list_model_calls(db, limit=limit, offset=offset)
    return ModelCallListPage(
        items=[model_call_to_list_item(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )
