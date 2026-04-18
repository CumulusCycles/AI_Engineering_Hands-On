from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error envelope for JSON responses and OpenAPI documentation."""

    detail: str = Field(description="Human-readable error message")
    code: str | None = Field(
        default=None,
        description="Optional stable code for clients (e.g. validation_error, http_404)",
    )
