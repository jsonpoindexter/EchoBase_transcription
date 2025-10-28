from __future__ import annotations

from pydantic import Field

from src.EchoBase_transcription.db.schemas.base import OrmBase


class RadioUnitBase(OrmBase):
    system_id: int
    unit_id: int = Field(..., ge=1)
    alias: str | None = Field(None, max_length=100)


class RadioUnitCreate(RadioUnitBase):
    pass


class RadioUnitRead(RadioUnitBase):
    id: int
