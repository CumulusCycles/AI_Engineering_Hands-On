import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.errors import ErrorResponse

logger = logging.getLogger(__name__)

_VALIDATION_DETAIL_MAX_PARTS = 25


def _validation_errors_detail(errors: list) -> str:
    """Format a list of pydantic validation errors into a semicolon-delimited summary string."""

    parts: list[str] = []
    for err in errors[:_VALIDATION_DETAIL_MAX_PARTS]:
        loc_parts = [str(x) for x in err.get("loc", ()) if x not in ("body",)]
        loc = ".".join(loc_parts) or "request"
        msg = err.get("msg", "Invalid input")
        parts.append(f"{loc}: {msg}")
    if not parts:
        return "Validation error"
    detail = "; ".join(parts)
    if len(errors) > _VALIDATION_DETAIL_MAX_PARTS:
        detail += f"; … and {len(errors) - _VALIDATION_DETAIL_MAX_PARTS} more"
    return detail


def _detail_to_str(detail: str | list | None) -> str:
    """Coerce an HTTPException detail (str, list, or None) to a single string."""

    if detail is None:
        return "Error"
    if isinstance(detail, str):
        return detail
    return "; ".join(str(x) for x in detail)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global HTTP, validation, and unhandled exception handlers to the app."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        """Convert Starlette HTTP exceptions into a uniform ErrorResponse JSON body."""

        body = ErrorResponse(
            detail=_detail_to_str(exc.detail),
            code=f"http_{exc.status_code}",
        ).model_dump()
        return JSONResponse(
            status_code=exc.status_code,
            content=body,
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Return a 422 ErrorResponse with a human-readable validation summary."""

        errors = exc.errors()
        detail = _validation_errors_detail(errors) if errors else "Validation error"
        body = ErrorResponse(detail=detail, code="validation_error").model_dump()
        return JSONResponse(status_code=422, content=body)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Log the traceback and return a generic 500 ErrorResponse."""

        logger.exception(
            "%s %s — unhandled exception",
            request.method,
            request.url.path,
            exc_info=exc,
        )
        body = ErrorResponse(
            detail="An unexpected error occurred",
            code="internal_error",
        ).model_dump()
        return JSONResponse(status_code=500, content=body)
