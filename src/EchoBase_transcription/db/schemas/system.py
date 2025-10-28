from __future__ import annotations

from sqlmodel import Field

from src.EchoBase_transcription.db.schemas.base import DTOBase
from src.EchoBase_transcription.db.models.system import SystemBase


class SystemCreate(SystemBase, DTOBase):
    """
    Body for creating a new System.

    SystemBase already defines:
      name: str
      description: str | None
    """
    pass


class SystemRead(SystemBase, DTOBase):
    """
    Payload we return to clients for a System.
    """

    id: int = Field(..., ge=1)
    # inherits: name, description
