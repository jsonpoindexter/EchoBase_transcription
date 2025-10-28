from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List

from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import UniqueConstraint, ForeignKey, Integer, String

if TYPE_CHECKING:
    from .system import System
    from .call import Call


class RadioUnitBase(SQLModel):
    """Shared attributes for RadioUnit used in create/read/update."""

    system_id: int = Field(
        sa_column=Column(
            ForeignKey("systems.id", ondelete="CASCADE"),
            nullable=False,
        )
    )

    unit_id: int = Field(
        sa_column=Column(Integer, nullable=False)
    )

    alias: Optional[str] = Field(
        default=None,
        sa_column=Column(String(100)),
    )


class RadioUnit(RadioUnitBase, table=True):
    """Individual subscriber radio (the 'from' ID)."""

    __tablename__ = "radio_units"
    __table_args__ = (
        UniqueConstraint("system_id", "unit_id", name="uq_system_unit"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    system: "System" = Relationship(back_populates="units")
    calls: List["Call"] = Relationship(back_populates="unit")
