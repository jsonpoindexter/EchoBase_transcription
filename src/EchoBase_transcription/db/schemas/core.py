from __future__ import annotations
from pydantic import Field

from .base import OrmBase


# ── System ────────────────────────────────────────────────────────────────
class SystemBase(OrmBase):
    name: str = Field(..., max_length=100)
    description: str | None = None


class SystemCreate(SystemBase):
    pass


class SystemRead(SystemBase):
    id: int


# ── TalkGroup ─────────────────────────────────────────────────────────────
class TalkGroupBase(OrmBase):
    system_id: int
    tg_number: int = Field(..., ge=1)
    alias: str | None = Field(None, max_length=100)
    whisper_prompt: str | None = None


class TalkGroupCreate(TalkGroupBase):
    pass


class TalkGroupRead(TalkGroupBase):
    id: int


# ── RadioUnit ─────────────────────────────────────────────────────────────
class RadioUnitBase(OrmBase):
    system_id: int
    unit_id: int = Field(..., ge=1)
    alias: str | None = Field(None, max_length=100)


class RadioUnitCreate(RadioUnitBase):
    pass


class RadioUnitRead(RadioUnitBase):
    id: int