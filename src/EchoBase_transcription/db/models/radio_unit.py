from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .system import System
    from .call import Call


class RadioUnitBase(SQLModel):
    """Shared attributes for RadioUnit used in create/read/update."""

    system_id: int = Field(foreign_key="systems.id")
    unit_id: int
    alias: Optional[str] = None


class RadioUnit(RadioUnitBase, table=True):
    """Individual subscriber radio (the 'from' ID)."""

    __tablename__ = "radio_units"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    system: "System" = Relationship(back_populates="units")
    calls: list["Call"] = Relationship(back_populates="unit")
