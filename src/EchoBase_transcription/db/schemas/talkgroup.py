from __future__ import annotations

from pydantic import Field

from src.EchoBase_transcription.db.schemas.base import OrmBase


class TalkGroupBase(OrmBase):
    system_id: int
    tg_number: int = Field(..., ge=1)
    alias: str | None = Field(None, max_length=100)
    whisper_prompt: str | None = None


class TalkGroupCreate(TalkGroupBase):
    pass


class TalkGroupRead(TalkGroupBase):
    id: int
