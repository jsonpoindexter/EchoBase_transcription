from __future__ import annotations

from datetime import datetime

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, Float, String, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    # These imports are ONLY for the type checker / IDE.
    # They do NOT run at runtime, so they do NOT create a cycle.
    from .system import System
    from .talkgroup import TalkGroup
    from .radio_unit import RadioUnit
    from .user import User


class Call(Base):
    """A single recorded radio transmission."""

    __tablename__ = "calls"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    system_id: Mapped[int] = mapped_column(
        ForeignKey("systems.id", ondelete="CASCADE"), nullable=False
    )
    talkgroup_id: Mapped[int | None] = mapped_column(
        ForeignKey("talkgroups.id", ondelete="SET NULL")
    )
    unit_id: Mapped[int | None] = mapped_column(
        ForeignKey("radio_units.id", ondelete="SET NULL")
    )

    # Timing & file info
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    duration: Mapped[float | None] = mapped_column(Float)
    audio_path: Mapped[str] = mapped_column(String(255), nullable=False)

    # ASR data
    transcript: Mapped[str | None] = mapped_column(Text)
    corrected_transcript: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    needs_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    transcriber: Mapped[str | None] = mapped_column(String(100))

    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Full-text search vector
    transcript_tsv: Mapped[str | None] = mapped_column(TSVECTOR)

    # Relationships
    system: Mapped["System"] = relationship(back_populates="calls")
    talkgroup: Mapped["TalkGroup"] = relationship(back_populates="calls")
    unit: Mapped["RadioUnit"] = relationship(back_populates="calls")
    reviewer: Mapped["User"] = relationship()

    __table_args__ = (
        Index("ix_calls_talkgroup_timestamp", "talkgroup_id", "timestamp"),
        Index("ix_calls_transcript_tsv", "transcript_tsv", postgresql_using="gin"),
    )
