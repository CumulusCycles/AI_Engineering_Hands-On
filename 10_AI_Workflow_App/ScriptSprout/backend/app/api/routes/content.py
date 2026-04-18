from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_owned_content_or_404, require_author
from app.api.openai_route_errors import (
    OPENAI_ROUTE_SDK_EXCEPTIONS,
    ensure_openai_client,
    http_exception_from_openai_route_error,
)
from app.api.query_params import OPTIONAL_STATUS_QUERY_DESCRIPTION, normalize_optional_query_str
from app.config import Settings
from app.db.deps import get_db
from app.db.models import ContentItem, User
from app.db.repos.audit_events import insert_audit_event
from app.db.repos.content_items import (
    count_content_items_for_author,
    create_content_item,
    list_content_items_for_author,
)
from app.schemas.audio_generation import GenerateAudioRequest, GenerateAudioResponse
from app.schemas.content import (
    ContentCreate,
    ContentItemDetail,
    ContentListPage,
    content_item_to_detail,
    content_item_to_list_item,
)
from app.schemas.semantic_index import UpsertSemanticIndexResponse
from app.schemas.story_generation import GenerateStoryResponse
from app.schemas.synopsis import (
    ApproveStepRequest,
    GenerateDescriptionResponse,
    GenerateSynopsisResponse,
    GenerateTitleResponse,
    RegenerateStepRequest,
)
from app.schemas.thumbnail_generation import GenerateThumbnailResponse
from app.services.audio_generation import run_generate_audio
from app.services.embedding_index import run_upsert_semantic_index
from app.services.story_generation import run_generate_story_and_guardrails
from app.services.synopsis_generation import run_generate_synopsis
from app.services.thumbnail_generation import run_generate_thumbnail
from app.services.title_description_generation import (
    run_generate_description,
    run_generate_title,
)

router = APIRouter(prefix="/api/content", tags=["content"])

# --- Content status constants ---
STATUS_STORY_GENERATED = "story_generated"
STATUS_GUARDRAILS_PASSED = "guardrails_passed"
STATUS_THUMBNAIL_GENERATED = "thumbnail_generated"
STATUS_AUDIO_GENERATED = "audio_generated"

# Statuses that allow thumbnail generation.
_THUMBNAIL_READY_STATUSES_GR = {STATUS_GUARDRAILS_PASSED}
_THUMBNAIL_READY_STATUSES_NO_GR = {STATUS_STORY_GENERATED}

# Statuses that allow audio generation.
_AUDIO_READY_STATUSES_GR = {
    STATUS_GUARDRAILS_PASSED, STATUS_THUMBNAIL_GENERATED, STATUS_AUDIO_GENERATED,
}
_AUDIO_READY_STATUSES_NO_GR = {
    STATUS_STORY_GENERATED, STATUS_THUMBNAIL_GENERATED, STATUS_AUDIO_GENERATED,
}

# Ordered pipeline steps; clearing from a step clears it and everything after it.
_DOWNSTREAM_FIELDS: list[tuple[str, ...]] = [
    ("title",),
    ("description",),
    ("story_text",),
    ("thumbnail_blob", "thumbnail_mime_type"),
    ("audio_blob", "audio_mime_type", "audio_voice", "audio_generated_at"),
]


def _clear_downstream(row: ContentItem, *, from_step: str) -> None:
    """Null out all content fields at and after *from_step* in the pipeline."""
    step_names = {fields[0]: i for i, fields in enumerate(_DOWNSTREAM_FIELDS)}
    start = step_names.get(from_step)
    if start is None:
        return
    for fields in _DOWNSTREAM_FIELDS[start:]:
        for field in fields:
            setattr(row, field, None)


def _resolve_tts_voice(settings: Settings, voice_key: str | None) -> str:
    """Map a logical voice key (e.g. 'female_us') to the configured TTS voice name."""

    voice_by_key = {
        "female_us": settings.tts_voice_female_us,
        "female_uk": settings.tts_voice_female_uk,
        "male_us": settings.tts_voice_male_us,
        "male_uk": settings.tts_voice_male_uk,
    }
    if voice_key is None:
        selected = settings.tts_voice_default
    else:
        selected = voice_by_key.get(voice_key)
        if selected is None:
            valid = ", ".join(sorted(voice_by_key))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown voice_key '{voice_key}'. Valid: {valid}.",
            )
    return selected.strip()


@router.post("/", response_model=ContentItemDetail, status_code=status.HTTP_201_CREATED)
def create_content_item_route(
    body: ContentCreate,
    user: Annotated[User, Depends(require_author)],
    db: Session = Depends(get_db),
) -> ContentItemDetail:
    """Create a new content item shell from the author's prompt."""

    row = create_content_item(db, author_id=user.id, **body.create_kwargs())
    return content_item_to_detail(row)


@router.get("/", response_model=ContentListPage)
def list_my_content(
    user: Annotated[User, Depends(require_author)],
    db: Session = Depends(get_db),
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    content_status: Annotated[
        str | None,
        Query(alias="status", max_length=64, description=OPTIONAL_STATUS_QUERY_DESCRIPTION),
    ] = None,
) -> ContentListPage:
    """Return a paginated list of the authenticated author's content items."""

    status_filter = normalize_optional_query_str(content_status)
    total = count_content_items_for_author(db, user.id, status=status_filter)
    rows = list_content_items_for_author(
        db,
        user.id,
        limit=limit,
        offset=offset,
        status=status_filter,
    )
    return ContentListPage(
        items=[content_item_to_list_item(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{content_id}", response_model=ContentItemDetail)
def get_content_item_route(
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
) -> ContentItemDetail:
    """Return full detail for a single owned content item."""

    return content_item_to_detail(row)


@router.get("/{content_id}/thumbnail")
def get_content_thumbnail(
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
) -> Response:
    """Serve the stored thumbnail image bytes, or 404 if not yet generated."""

    if row.thumbnail_blob is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail not available",
        )
    media_type = row.thumbnail_mime_type or "application/octet-stream"
    return Response(content=bytes(row.thumbnail_blob), media_type=media_type)


@router.get("/{content_id}/audio")
def get_content_audio(
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
) -> Response:
    """Serve the stored audio bytes, or 404 if not yet generated."""

    if row.audio_blob is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio not available",
        )
    media_type = row.audio_mime_type or "audio/mpeg"
    return Response(content=bytes(row.audio_blob), media_type=media_type)


@router.post("/{content_id}/generate-synopsis", response_model=GenerateSynopsisResponse)
def generate_synopsis_route(
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
    user: Annotated[User, Depends(require_author)],
    request: Request,
    db: Session = Depends(get_db),
) -> GenerateSynopsisResponse:
    """Call OpenAI to generate a synopsis from the content's source prompt."""

    settings = request.app.state.settings

    client = ensure_openai_client(settings)

    _clear_downstream(row, from_step="title")

    try:
        resp = run_generate_synopsis(
            client=client,
            model=settings.openai_synopsis_model,
            content=row,
            max_attempts=settings.transient_retry_max_attempts,
            db=db,
            user_id=user.id,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(exc) from exc

    insert_audit_event(
        db,
        user_id=user.id,
        event_type="generate_synopsis",
        entity_type="content_item",
        entity_id=row.id,
        payload={"synopsis": row.synopsis},
    )
    db.commit()
    db.refresh(row)

    return resp


@router.post("/{content_id}/generate-title", response_model=GenerateTitleResponse)
def generate_title_route(
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
    user: Annotated[User, Depends(require_author)],
    request: Request,
    db: Session = Depends(get_db),
) -> GenerateTitleResponse:
    """Call OpenAI to generate a title from the content's synopsis."""

    settings = request.app.state.settings

    if row.synopsis is None or not row.synopsis.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No synopsis to generate title",
        )

    client = ensure_openai_client(settings)

    _clear_downstream(row, from_step="description")

    try:
        resp = run_generate_title(
            client=client,
            model=settings.openai_title_model,
            content=row,
            max_attempts=settings.transient_retry_max_attempts,
            db=db,
            user_id=user.id,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(exc) from exc

    insert_audit_event(
        db,
        user_id=user.id,
        event_type="generate_title",
        entity_type="content_item",
        entity_id=row.id,
        payload={"title": row.title},
    )
    db.commit()
    db.refresh(row)

    return resp


@router.post("/{content_id}/generate-description", response_model=GenerateDescriptionResponse)
def generate_description_route(
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
    user: Annotated[User, Depends(require_author)],
    request: Request,
    db: Session = Depends(get_db),
) -> GenerateDescriptionResponse:
    """Call OpenAI to generate a YouTube description from the synopsis and title."""

    settings = request.app.state.settings

    if row.synopsis is None or not row.synopsis.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No synopsis to generate description",
        )
    if row.title is None or not row.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No title to generate description",
        )

    client = ensure_openai_client(settings)

    _clear_downstream(row, from_step="story_text")

    try:
        resp = run_generate_description(
            client=client,
            model=settings.openai_description_model,
            content=row,
            max_attempts=settings.transient_retry_max_attempts,
            db=db,
            user_id=user.id,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(exc) from exc

    insert_audit_event(
        db,
        user_id=user.id,
        event_type="generate_description",
        entity_type="content_item",
        entity_id=row.id,
        payload={"description": row.description},
    )
    db.commit()
    db.refresh(row)

    return resp


@router.post("/{content_id}/generate-story", response_model=GenerateStoryResponse)
def generate_story_route(
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
    user: Annotated[User, Depends(require_author)],
    request: Request,
    db: Session = Depends(get_db),
) -> GenerateStoryResponse:
    """Call OpenAI to generate the full story text and run guardrails."""

    settings = request.app.state.settings

    if row.synopsis is None or not row.synopsis.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No synopsis to generate story",
        )
    if row.title is None or not row.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No title to generate story",
        )
    if row.description is None or not row.description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No description to generate story",
        )

    client = ensure_openai_client(settings)

    _clear_downstream(row, from_step="thumbnail_blob")

    try:
        resp = run_generate_story_and_guardrails(
            client=client,
            model_story=settings.openai_story_model,
            model_guardrails=settings.openai_guardrails_model,
            content=row,
            max_attempts=settings.transient_retry_max_attempts,
            db=db,
            user_id=user.id,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(exc) from exc

    insert_audit_event(
        db,
        user_id=user.id,
        event_type="generate_story",
        entity_type="content_item",
        entity_id=row.id,
        payload={"status": row.status},
    )
    db.commit()
    db.refresh(row)

    return resp


@router.post("/{content_id}/generate-thumbnail", response_model=GenerateThumbnailResponse)
def generate_thumbnail_route(
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
    user: Annotated[User, Depends(require_author)],
    request: Request,
    db: Session = Depends(get_db),
) -> GenerateThumbnailResponse:
    """Call DALL-E to generate a thumbnail image from the story text."""

    settings = request.app.state.settings

    if row.story_text is None or not row.story_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No story to generate thumbnail",
        )

    # Prevent regeneration if thumbnail already exists
    if row.thumbnail_blob is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thumbnail already generated for this content.",
        )

    # Guardrails gate: if enabled, require a pass before generating a thumbnail.
    if row.guardrails_enabled and row.status not in _THUMBNAIL_READY_STATUSES_GR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guardrails must pass before generating thumbnail",
        )
    if not row.guardrails_enabled and row.status not in _THUMBNAIL_READY_STATUSES_NO_GR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story must be generated before thumbnail",
        )

    client = ensure_openai_client(settings)

    try:
        resp, image_bytes = run_generate_thumbnail(
            client=client,
            model_image=settings.openai_image_model,
            size=settings.thumbnail_size,
            quality=settings.thumbnail_quality,
            style=settings.thumbnail_style,
            content=row,
            max_attempts=settings.transient_retry_max_attempts,
            db=db,
            user_id=user.id,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(exc) from exc

    # Persist bytes; serve/fetch endpoints are separate.
    row.thumbnail_blob = image_bytes
    row.thumbnail_mime_type = resp.thumbnail_mime_type
    row.status = STATUS_THUMBNAIL_GENERATED

    insert_audit_event(
        db,
        user_id=user.id,
        event_type="generate_thumbnail",
        entity_type="content_item",
        entity_id=row.id,
        payload={"status": row.status, "mime": row.thumbnail_mime_type},
    )
    db.commit()
    db.refresh(row)

    return resp


@router.post("/{content_id}/generate-audio", response_model=GenerateAudioResponse)
def generate_audio_route(
    body: GenerateAudioRequest,
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
    user: Annotated[User, Depends(require_author)],
    request: Request,
    db: Session = Depends(get_db),
) -> GenerateAudioResponse:
    """Call OpenAI TTS to generate audio narration of the story text."""

    settings = request.app.state.settings

    if row.story_text is None or not row.story_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No story to generate audio",
        )

    # Prevent regeneration if audio already exists
    if row.audio_blob is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio already generated for this content.",
        )

    if row.guardrails_enabled and row.status not in _AUDIO_READY_STATUSES_GR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guardrails must pass before generating audio",
        )
    if not row.guardrails_enabled and row.status not in _AUDIO_READY_STATUSES_NO_GR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story must be generated before audio",
        )

    selected_voice = _resolve_tts_voice(settings, body.voice_key)
    if not selected_voice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Configured audio voice is blank",
        )

    client = ensure_openai_client(settings)

    try:
        result = run_generate_audio(
            db=db,
            user_id=user.id,
            story_text=row.story_text,
            client=client,
            model_name=settings.openai_tts_model,
            voice=selected_voice,
            max_attempts=settings.transient_retry_max_attempts,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(exc) from exc

    row.audio_blob = result.audio_bytes
    row.audio_mime_type = "audio/mpeg"
    row.audio_voice = selected_voice
    row.audio_generated_at = datetime.now(UTC)
    row.status = STATUS_AUDIO_GENERATED

    insert_audit_event(
        db,
        user_id=user.id,
        event_type="generate_audio",
        entity_type="content_item",
        entity_id=row.id,
        payload={"status": row.status, "voice": row.audio_voice},
    )
    db.commit()
    db.refresh(row)

    return GenerateAudioResponse.from_bytes(
        content_id=row.id,
        attempts_used=result.attempts_used,
        audio_voice=selected_voice,
        audio_bytes=result.audio_bytes,
        openai_audio_response_id=result.openai_response_id,
    )


@router.post("/{content_id}/approve-step", response_model=ContentItemDetail)
def approve_step_route(
    body: ApproveStepRequest,
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
    user: Annotated[User, Depends(require_author)],
    db: Session = Depends(get_db),
) -> ContentItemDetail:
    """Handle the API request and return a typed response.

    Args:
        body: Validated request payload.
        row: Database model row used to build a schema response.
        user: Authenticated user for authorization and ownership checks.
        db: Active database session for repository operations.

    Returns:
        Result generated for the caller.

    """

    if body.step == "synopsis":
        if row.synopsis is None or not row.synopsis.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No synopsis to approve",
            )
        row.status = "synopsis_approved"
        event_type = "approve_synopsis"
        payload = {"synopsis": row.synopsis}
    elif body.step == "title":
        if row.title is None or not row.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No title to approve",
            )
        row.status = "title_approved"
        event_type = "approve_title"
        payload = {"title": row.title}
    elif body.step == "description":
        if row.description is None or not row.description.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No description to approve",
            )
        row.status = "description_approved"
        event_type = "approve_description"
        payload = {"description": row.description}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported step")

    insert_audit_event(
        db,
        user_id=user.id,
        event_type=event_type,
        entity_type="content_item",
        entity_id=row.id,
        payload=payload,
    )
    db.commit()
    db.refresh(row)

    return content_item_to_detail(row)


@router.post("/{content_id}/regenerate-step", response_model=ContentItemDetail)
def regenerate_step_route(  # noqa: C901
    body: RegenerateStepRequest,
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
    user: Annotated[User, Depends(require_author)],
    request: Request,
    db: Session = Depends(get_db),
) -> ContentItemDetail:
    """Handle the API request and return a typed response.

    Args:
        body: Validated request payload.
        row: Database model row used to build a schema response.
        user: Authenticated user for authorization and ownership checks.
        request: Incoming HTTP request context.
        db: Active database session for repository operations.

    Returns:
        Result generated for the caller.

    """

    if body.step not in ("synopsis", "title", "description"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported step")

    settings = request.app.state.settings

    client = ensure_openai_client(settings)

    if body.step == "synopsis":
        if row.source_prompt is None or not row.source_prompt.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No source prompt to regenerate synopsis",
            )

        _clear_downstream(row, from_step="title")

        try:
            run_generate_synopsis(
                client=client,
                model=settings.openai_synopsis_model,
                content=row,
                max_attempts=settings.transient_retry_max_attempts,
                db=db,
                user_id=user.id,
            )
        except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
            raise http_exception_from_openai_route_error(exc) from exc

        event_type = "regenerate_synopsis"
        payload = {"synopsis": row.synopsis}

    elif body.step == "title":
        if row.synopsis is None or not row.synopsis.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No synopsis to regenerate title",
            )

        _clear_downstream(row, from_step="description")

        try:
            run_generate_title(
                client=client,
                model=settings.openai_title_model,
                content=row,
                max_attempts=settings.transient_retry_max_attempts,
                db=db,
                user_id=user.id,
            )
        except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
            raise http_exception_from_openai_route_error(exc) from exc

        event_type = "regenerate_title"
        payload = {"title": row.title}

    else:  # body.step == "description"
        if row.synopsis is None or not row.synopsis.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No synopsis to regenerate description",
            )
        if row.title is None or not row.title.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No title to regenerate description",
            )

        _clear_downstream(row, from_step="story_text")

        try:
            run_generate_description(
                client=client,
                model=settings.openai_description_model,
                content=row,
                max_attempts=settings.transient_retry_max_attempts,
                db=db,
                user_id=user.id,
            )
        except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
            raise http_exception_from_openai_route_error(exc) from exc

        event_type = "regenerate_description"
        payload = {"description": row.description}

    insert_audit_event(
        db,
        user_id=user.id,
        event_type=event_type,
        entity_type="content_item",
        entity_id=row.id,
        payload=payload,
    )
    db.commit()
    db.refresh(row)

    return content_item_to_detail(row)


@router.post(
    "/{content_id}/semantic-index",
    response_model=UpsertSemanticIndexResponse,
    summary="Upsert semantic index vector (title + description + story)",
    description=(
        "Calls OpenAI embeddings on title, description, and story text only, then upserts into "
        "Chroma `content_semantic_index` with metadata. "
        "Audio and thumbnail bytes are never embedded."
    ),
)
def upsert_semantic_index_route(
    row: Annotated[ContentItem, Depends(get_owned_content_or_404)],
    user: Annotated[User, Depends(require_author)],
    request: Request,
    db: Session = Depends(get_db),
) -> UpsertSemanticIndexResponse:
    """Handle the API request and return a typed response.

    Args:
        row: Database model row used to build a schema response.
        user: Authenticated user for authorization and ownership checks.
        request: Incoming HTTP request context.
        db: Active database session for repository operations.

    Returns:
        Result generated for the caller.

    """

    settings = request.app.state.settings
    collection = request.app.state.chroma_collection

    if row.title is None or not row.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title is required to build the semantic index document",
        )
    if row.description is None or not row.description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Description is required to build the semantic index document",
        )
    if row.story_text is None or not row.story_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Story text is required to build the semantic index document",
        )

    client = ensure_openai_client(settings)

    try:
        attempts_used, model_used, doc_count = run_upsert_semantic_index(
            client=client,
            embedding_model=settings.openai_embedding_model,
            collection=collection,
            content=row,
            max_attempts=settings.transient_retry_max_attempts,
            db=db,
            user_id=user.id,
        )
    except OPENAI_ROUTE_SDK_EXCEPTIONS as exc:
        raise http_exception_from_openai_route_error(exc) from exc

    insert_audit_event(
        db,
        user_id=user.id,
        event_type="upsert_semantic_index",
        entity_type="content_item",
        entity_id=row.id,
        payload={
            "embedding_model": model_used,
            "chroma_document_id": str(row.id),
            "attempts_used": attempts_used,
            "collection_document_count": doc_count,
        },
    )
    db.commit()

    return UpsertSemanticIndexResponse(
        content_id=row.id,
        embedding_model=model_used,
        chroma_document_id=str(row.id),
        attempts_used=attempts_used,
        collection_document_count=doc_count,
    )
