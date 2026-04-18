from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Service liveness payload."""

    status: Literal["ok"] = Field(description="Always 'ok' when the process is serving requests")
    service: str = Field(description="Logical service name")
