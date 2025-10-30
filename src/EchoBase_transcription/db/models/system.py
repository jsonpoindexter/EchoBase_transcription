from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .call import Call
    from .radio_unit import RadioUnit
    from .talkgroup import TalkGroup


class SystemBase(SQLModel):
    """Shared attributes for System used in create/read/update."""

    name: str
    description: Optional[str] = None


class System(SystemBase, table=True):
    """Database model for a radio system or network (e.g. county‑wide P25)."""

    __tablename__ = "systems"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    calls: list["Call"] = Relationship(back_populates="system")
    units: list["RadioUnit"] = Relationship(back_populates="system")
    talkgroups: list["TalkGroup"] = Relationship(back_populates="system")
