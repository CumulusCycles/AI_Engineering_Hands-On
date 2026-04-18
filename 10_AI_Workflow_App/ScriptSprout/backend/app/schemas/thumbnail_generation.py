from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GenerateThumbnailResponse(BaseModel):
    """Thumbnail generation response."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "content_id": 1,
                    "status": "thumbnail_generated",
                    "attempts_used": 1,
                    "thumbnail_mime_type": "image/png",
                    "thumbnail_bytes_base64": "iVBORw0K...",
                }
            ]
        }
    )

    content_id: int
    status: Literal["thumbnail_generated"]
    attempts_used: int = Field(ge=1)
    thumbnail_mime_type: str = "image/png"
    thumbnail_bytes_base64: str
    openai_image_response_id: str | None = None

