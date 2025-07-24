from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Text, Integer, ForeignKey, UniqueConstraint, DateTime, Float, Boolean, Index
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base


class System(Base):
    """A radio system or network (e.g. county‑wide P25)."""

    __tablename__ = "systems"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    talkgroups: Mapped[list["TalkGroup"]] = relationship(
        back_populates="system", cascade="all, delete-orphan"
    )
    units: Mapped[list["RadioUnit"]] = relationship(
        back_populates="system", cascade="all, delete-orphan"
    )
    calls: Mapped[list["Call"]] = relationship(back_populates="system")


class TalkGroup(Base):
    """A talk‑group / channel within a system."""

    __tablename__ = "talkgroups"
    __table_args__ = (
        UniqueConstraint("system_id", "tg_number", name="uq_system_tg"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    system_id: Mapped[int] = mapped_column(
        ForeignKey("systems.id", ondelete="CASCADE"), nullable=False
    )
    tg_number: Mapped[int] = mapped_column(Integer, nullable=False)
    alias: Mapped[str | None] = mapped_column(String(100))
    whisper_prompt: Mapped[str | None] = mapped_column(Text)

    # Relationships
    system: Mapped["System"] = relationship(back_populates="talkgroups")
    calls: Mapped[list["Call"]] = relationship(back_populates="talkgroup")


class RadioUnit(Base):
    """Individual subscriber radio (the ‘from’ ID)."""

    __tablename__ = "radio_units"
    __table_args__ = (
        UniqueConstraint("system_id", "unit_id", name="uq_system_unit"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    system_id: Mapped[int] = mapped_column(
        ForeignKey("systems.id", ondelete="CASCADE"), nullable=False
    )
    unit_id: Mapped[int] = mapped_column(Integer, nullable=False)
    alias: Mapped[str | None] = mapped_column(String(100))

    # Relationships
    system: Mapped["System"] = relationship(back_populates="units")
    calls: Mapped[list["Call"]] = relationship(back_populates="unit")


class User(Base):
    """Future‑use: API / UI user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    api_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

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
