from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    # These imports are ONLY for the type checker / IDE.
    # They do NOT run at runtime, so they do NOT create a cycle.
    from .system import System
    from .call import Call


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
