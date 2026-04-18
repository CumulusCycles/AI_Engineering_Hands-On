from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import require_author
from app.api.openai_route_errors import (
    OPENAI_ROUTE_SDK_EXCEPTIONS,
    ensure_openai_client,
    http_exception_from_openai_route_error,
)
from app.db.deps import get_db
from app.db.models import User
from app.schemas.story_parameters import (
    ExtractStoryParametersRequest,
    StoryParametersExtractResponse,
)
from app.services.story_parameter_extraction import run_extract_story_parameters

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/nlp", tags=["nlp"])


@router.post(
    "/extract-story-parameters",
    response_model=StoryParametersExtractResponse,
    summary="Extract story parameters from a prompt (author)",
    description=(
        "Uses OpenAI **`responses.parse`** with a structured schema for **subject**, **genre**, "
        "**age_group**, **video_length_minutes**, and optional **target_word_count**. "
        "Returns **missing_fields**, **is_complete**, and **`follow_up`**: "
        "UI-ready questions per missing slot (`question`, `input_kind`, optional "
        "`suggested_options`). **Admins** receive **403**. Retries use "
        "**`TRANSIENT_RETRY_MAX_ATTEMPTS`**; attempts are logged to **`model_calls`**."
    ),
)
def extract_story_parameters_route(
    body: ExtractStoryParametersRequest,
    user: Annotated[User, Depends(require_author)],
    request: Request,
    db: Session = Depends(get_db),
) -> StoryParametersExtractResponse:
    """Handle the API request and return a typed response.

    Args:
        body: Validated request payload.
        user: Authenticated user for authorization and ownership checks.
        request: Incoming HTTP request context.
        db: Active database session for repository operations.

    Returns:
        Result generated for the caller.

    """

    settings = request.app.state.settings
    client = ensure_openai_client(settings)

    try:
        return run_extract_story_parameters(
            client=client,
            model=settings.openai_nlp_model,
            user_prompt=body.prompt,
            max_attempts=settings.transient_retry_max_attempts,
            db=db,
            user_id=user.id,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(
            exc,
            logger=logger,
            log_context="extract_story_parameters",
            runtime_error_detail="Could not parse structured parameters from model output",
            openai_error_log_message="extract_story_parameters failed",
        ) from exc
