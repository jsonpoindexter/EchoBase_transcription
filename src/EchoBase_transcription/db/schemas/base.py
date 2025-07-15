from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class OrmBase(BaseModel):
    """Base for all DTOs – Pydantic v2."""

    model_config = {
        "from_attributes": True,          # allow .model_validate(orm_obj)
        "populate_by_name": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }


# Common pagination wrapper
class Page(OrmBase):
    items: list[Any]
    total: int
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=500)