from __future__ import annotations

from datetime import datetime
from pydantic import Field, constr, confloat

from .base import OrmBase


# ── Create / ingest (used by worker) ──────────────────────────────────────
class CallCreate(OrmBase):
    system_id: int
    talkgroup_id: int | None = None
    unit_id: int | None = None

    timestamp: datetime
    duration: float = Field(..., gt=0, description="Seconds")
    audio_path: str

    transcript: str | None = None
    confidence: confloat(ge=-10.0, le=0.0) | None = None
    needs_review: bool = False
    transcriber: str | None = None


# ── Read-only representation ──────────────────────────────────────────────
class CallRead(CallCreate):
    id: int
    corrected_transcript: str | None = None
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None


# ── PATCH body for human correction --------------------------------------
class CallPatch(OrmBase):
    corrected_transcript: constr(strip_whitespace=True, min_length=1) | None = None
    needs_review: bool | None = None


# ── Search / filter params (parsed from query or JSON) --------------------
class CallSearch(OrmBase):
    system_id: int | None = None
    talkgroup_id: int | None = None
    unit_id: int | None = None
    since: datetime | None = None
    until: datetime | None = None
    min_confidence: float | None = None
    max_confidence: float | None = None
    text: str | None = None     # full-text search query
    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=500)