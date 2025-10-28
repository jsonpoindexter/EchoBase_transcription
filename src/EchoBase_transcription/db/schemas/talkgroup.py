from __future__ import annotations

from sqlmodel import Field

from src.EchoBase_transcription.db.schemas.base import DTOBase
from src.EchoBase_transcription.db.models.talkgroup import TalkGroupBase


class TalkGroupCreate(TalkGroupBase, DTOBase):
    """
    Body for creating a TalkGroup.

    TalkGroupBase already defines:
      system_id: int
      tg_number: int
      alias: str | None
      whisper_prompt: str | None
    """
    pass


class TalkGroupRead(TalkGroupBase, DTOBase):
    """
    Payload we return to clients for a TalkGroup.
    """

    id: int = Field(..., ge=1)
