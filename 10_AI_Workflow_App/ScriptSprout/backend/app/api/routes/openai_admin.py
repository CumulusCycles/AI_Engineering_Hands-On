from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.api.openai_route_errors import (
    OPENAI_ROUTE_SDK_EXCEPTIONS,
    ensure_openai_client,
    http_exception_from_openai_route_error,
)
from app.db.deps import get_db
from app.db.models import User
from app.schemas.openai_smoke import OpenAiSmokeRequest, OpenAiSmokeResponse
from app.services.responses_smoke import run_responses_smoke

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/openai", tags=["admin"])


@router.post(
    "/smoke",
    response_model=OpenAiSmokeResponse,
    summary="OpenAI Responses smoke (admin)",
    description=(
        "Calls the OpenAI **Responses** API with a short prompt and returns a **normalized** "
        "payload. **Transient** errors (e.g. 429, 5xx, connection issues) are retried up to "
        "`TRANSIENT_RETRY_MAX_ATTEMPTS` (**2** by default = one retry). "
        "Requires `OPENAI_API_KEY` in the repo-root `.env`. Authors receive **403**. "
        "Each SDK attempt is logged to **`model_calls`**."
    ),
)
def openai_smoke(
    body: OpenAiSmokeRequest,
    user: Annotated[User, Depends(require_admin)],
    request: Request,
    db: Session = Depends(get_db),
) -> OpenAiSmokeResponse:
    """Run an OpenAI Responses smoke test and return the normalized result."""

    settings = request.app.state.settings
    client = ensure_openai_client(settings)

    try:
        return run_responses_smoke(
            client=client,
            model=settings.openai_smoke_model,
            user_prompt=body.prompt,
            max_attempts=settings.transient_retry_max_attempts,
            db=db,
            user_id=user.id,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(
            exc,
            logger=logger,
            log_context="openai_smoke",
            openai_error_log_message="OpenAI smoke failed",
        ) from exc
