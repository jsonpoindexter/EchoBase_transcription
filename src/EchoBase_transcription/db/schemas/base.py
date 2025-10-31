from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlmodel import SQLModel, Field


class DTOBase(SQLModel):
    """
    Base for all request/response DTOs.

    Uses SQLModel so:
    - We get Pydantic-style validation / .model_dump()
    - We stay consistent with our SQLModel ORM classes
    - But these DTOs are NOT database tables (no table=True)
    """

    # Pydantic v2-style model_config. SQLModel passes this through.
    model_config = {
        # accept ORM instances directly (so we can do DTO.model_validate(db_obj))
        "from_attributes": True,
        # allow "alias" and field name to both work when constructing
        "populate_by_name": True,
        # nice datetime serialization
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }


class Page(DTOBase):
    """Generic pagination wrapper for list endpoints."""

    items: list[Any]
    total: int
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=500)
