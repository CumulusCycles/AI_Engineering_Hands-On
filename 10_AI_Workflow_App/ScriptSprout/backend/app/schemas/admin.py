from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AdminPingResponse(BaseModel):
    """Minimal admin-only payload for RBAC demos."""

    scope: Literal["admin"] = "admin"
    message: str = Field(default="ok")


class AdminCleanseRequest(BaseModel):
    """Destructive admin request confirmation payload."""

    confirm: bool = Field(
        default=False,
        description="Must be true to confirm the DB + vectorstore will be wiped.",
    )


class AdminCleanseResponse(BaseModel):
    """Report what the admin cleanse endpoint wiped."""

    ok: bool = True
    reseeded_admin: bool
    cleared: dict[str, int]
    chroma_wiped: bool
