from __future__ import annotations

from datetime import datetime
from sqlmodel import Field

from .base import DTOBase


# ── Create / ingest (used by worker / Celery) ─────────────────────────────
class CallCreate(DTOBase):
    """
    Body provided when ingesting a new recorded call.
    This is what the transcribe worker will build first.
    """

    system_id: int
    talkgroup_id: int | None = None
    unit_id: int | None = None

    timestamp: datetime
    duration: float = Field(..., gt=0, description="Seconds of audio in this call/PTT")
    audio_path: str

    # ASR output at ingest time
    transcript: str | None = None
    confidence: float | None = None
    needs_review: bool = False
    transcriber: str | None = None


# ── Read-only representation (API responses / UI) ────────────────────────
class CallRead(CallCreate):
    id: int = Field(..., ge=1)

    corrected_transcript: str | None = None
    reviewed_by: int | None = None
    reviewed_at: datetime | None = None


# ── PATCH body for human correction --------------------------------------
class CallPatch(DTOBase):
    corrected_transcript: str | None = Field(
        default=None,
        min_length=1,
        description="Human-edited transcript override",
    )
    needs_review: bool | None = None


# ── Search / filter params (query payload / request body) -----------------
class CallSearch(DTOBase):
    system_id: int | None = None
    talkgroup_id: int | None = None
    unit_id: int | None = None

    since: datetime | None = None
    until: datetime | None = None

    min_confidence: float | None = None
    max_confidence: float | None = None

    text: str | None = None  # full-text search query (tsvector match, etc.)

    page: int = Field(1, ge=1)
    per_page: int = Field(50, ge=1, le=500)
