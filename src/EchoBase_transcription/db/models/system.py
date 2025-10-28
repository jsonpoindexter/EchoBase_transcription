from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    # These imports are ONLY for the type checker / IDE.
    # They do NOT run at runtime, so they do NOT create a cycle.
    from .call import Call
    from .radio_unit import RadioUnit
    from .talkgroup import TalkGroup


class System(Base):
    """A radio system or network (e.g. county‑wide P25)."""
    calls: Mapped[list["Call"]] = relationship(back_populates="system")
    units: Mapped[list["RadioUnit"]] = relationship(
        back_populates="system", cascade="all, delete-orphan"
    )
    talkgroups: Mapped[list["TalkGroup"]] = relationship(
        back_populates="system", cascade="all, delete-orphan"
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    id: Mapped[int] = mapped_column(primary_key=True)
    __tablename__ = "systems"
