"""Pydantic models shared by API responses and OpenAPI."""

from app.schemas.errors import ErrorResponse
from app.schemas.health import HealthResponse

__all__ = ["ErrorResponse", "HealthResponse"]
