from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.db.models import ModelCall


class ModelCallListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: int | None
    user_id: int
    operation_type: str
    model_name: str
    purpose: str
    attempt_index: int
    success: bool
    latency_ms: int
    token_input: int | None
    token_output: int | None
    error_type: str | None
    created_at: datetime


class ModelCallListPage(BaseModel):
    items: list[ModelCallListItem]
    total: int
    limit: int
    offset: int


def model_call_to_list_item(row: ModelCall) -> ModelCallListItem:
    """Convert a ModelCall DB row to a ModelCallListItem schema."""

    return ModelCallListItem.model_validate(row)
