"""Typed event payloads used on the pub/sub bus."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field
from ..db.schemas.base import DTOBase

class CallEvent(DTOBase):
    call_id: int = Field(..., validation_alias="id")
    system_id: int
    talkgroup_id: int | None = None
    unit_id: int | None = None
    timestamp: datetime
    duration: float | None = None
    transcript: str | None = None
    corrected_transcript: str | None = None
    confidence: float | None = None
    needs_review: bool
    transcriber: str | None = None
    reviewed_at: datetime | None = None
    reviewed_by: int | None = None


class Heartbeat(BaseModel):
    """Periodic ping so you can monitor worker health."""

    type: Literal["worker.heartbeat"] = "worker.heartbeat"
    worker_id: str
    ts: datetime