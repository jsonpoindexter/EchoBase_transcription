from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import UniqueConstraint, ForeignKey, Integer, String, Text

if TYPE_CHECKING:
    from .system import System
    from .call import Call


class TalkGroupBase(SQLModel):
    """Shared attributes for TalkGroup used in create/read/update."""

    system_id: int = Field(
        sa_column=Column(
            ForeignKey("systems.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    tg_number: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    alias: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100)),
    )

    whisper_prompt: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
    )


class TalkGroup(TalkGroupBase, table=True):
    """A talk‑group / channel within a system."""

    __tablename__ = "talkgroups"
    __table_args__ = (
        UniqueConstraint("system_id", "tg_number", name="uq_system_tg"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    system: "System" = Relationship(back_populates="talkgroups")
    calls: List["Call"] = Relationship(back_populates="talkgroup")
