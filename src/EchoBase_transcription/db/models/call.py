from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import DateTime, Float, String, Text, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import TSVECTOR

if TYPE_CHECKING:
    from .system import System
    from .talkgroup import TalkGroup
    from .radio_unit import RadioUnit
    from .user import User


class CallBase(SQLModel):
    """Shared attributes for Call used in create/read/update."""

    timestamp: datetime = Field(
        sa_column=Column(DateTime(timezone=True), index=True, nullable=False)
    )

    duration: Optional[float] = Field(
        default=None,
        sa_column=Column(Float),
        description="Seconds of audio",
    )

    audio_path: str = Field(
        sa_column=Column(String(255), nullable=False)
    )

    # ASR data
    transcript: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
    )
    corrected_transcript: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
    )
    confidence: Optional[float] = Field(
        default=None,
        sa_column=Column(Float),
    )
    needs_review: bool = Field(
        default=False,
        sa_column=Column(Boolean, nullable=False, default=False),
    )
    transcriber: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100)),
    )

    reviewed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
    )

    # Postgres full‑text search vector
    transcript_tsv: Optional[str] = Field(
        default=None,
        sa_column=Column(TSVECTOR),
    )


class Call(CallBase, table=True):
    """Database model for a single recorded radio transmission (one PTT)."""

    __tablename__ = "calls"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    system_id: int = Field(
        sa_column=Column(
            ForeignKey("systems.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    talkgroup_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            ForeignKey("talkgroups.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    unit_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            ForeignKey("radio_units.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )

    reviewed_by: Optional[int] = Field(
        default=None,
        sa_column=Column(
            ForeignKey("users.id"),
            nullable=True,
        ),
    )

    # Relationships
    system: "System" = Relationship(back_populates="calls")
    talkgroup: Optional["TalkGroup"] = Relationship(back_populates="calls")
    unit: Optional["RadioUnit"] = Relationship(back_populates="calls")
    reviewer: Optional["User"] = Relationship()

    # Indexes / table args
    __table_args__ = (
        Index("ix_calls_talkgroup_timestamp", "talkgroup_id", "timestamp"),
        Index(
            "ix_calls_transcript_tsv",
            "transcript_tsv",
            postgresql_using="gin",
        ),
    )
