from __future__ import annotations

from pydantic import Field

from src.EchoBase_transcription.db.schemas.base import OrmBase


class SystemBase(OrmBase):
    name: str = Field(..., max_length=100)
    description: str | None = None


class SystemCreate(SystemBase):
    pass


class SystemRead(SystemBase):
    id: int
