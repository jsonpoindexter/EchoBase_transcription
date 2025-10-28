from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import String, Text

if TYPE_CHECKING:
    from .call import Call
    from .radio_unit import RadioUnit
    from .talkgroup import TalkGroup


class SystemBase(SQLModel):
    """Shared attributes for System used in create/read/update."""

    name: str = Field(
        sa_column=Column(String(100), unique=True, nullable=False)
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
    )


class System(SystemBase, table=True):
    """Database model for a radio system or network (e.g. county‑wide P25)."""

    __tablename__ = "systems"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    calls: List["Call"] = Relationship(back_populates="system")
    units: List["RadioUnit"] = Relationship(back_populates="system")
    talkgroups: List["TalkGroup"] = Relationship(back_populates="system")
