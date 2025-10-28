from __future__ import annotations

from sqlmodel import Field

from src.EchoBase_transcription.db.schemas.base import DTOBase
from src.EchoBase_transcription.db.models.radio_unit import RadioUnitBase


class RadioUnitCreate(RadioUnitBase, DTOBase):
    """
    Body for creating a RadioUnit (a subscriber/unit ID on the system).

    RadioUnitBase already defines:
      system_id: int
      unit_id: int
      alias: str | None
    """
    pass


class RadioUnitRead(RadioUnitBase, DTOBase):
    """
    Payload we return to clients for a RadioUnit.
    """

    id: int = Field(..., ge=1)
