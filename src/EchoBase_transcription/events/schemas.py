"""Typed event payloads used on the pub/sub bus."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CallEvent(BaseModel):
    """Emitted when a radio call has been transcribed."""

    type: Literal["call.transcribed"] = "call.transcribed"
    call_id: int
    system_id: int
    talkgroup_id: Optional[int] = None
    unit_id: Optional[int] = None
    timestamp: datetime
    duration: float
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    needs_review: bool
    transcript: Optional[str]

    # Convenience for SSE filters (string alias)
    talkgroup_alias: Optional[str] = None
    system_name: Optional[str] = None


class Heartbeat(BaseModel):
    """Periodic ping so you can monitor worker health."""

    type: Literal["worker.heartbeat"] = "worker.heartbeat"
    worker_id: str
    ts: datetime