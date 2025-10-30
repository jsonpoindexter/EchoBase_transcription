from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .system import System
    from .call import Call


class TalkGroupBase(SQLModel):
    """Shared attributes for TalkGroup used in create/read/update."""

    system_id: int = Field(foreign_key="systems.id")
    tg_number: int
    alias: Optional[str] = None
    whisper_prompt: Optional[str] = None


class TalkGroup(TalkGroupBase, table=True):
    """A talk‑group / channel within a system."""

    __tablename__ = "talkgroups"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    system: "System" = Relationship(back_populates="talkgroups")
    calls: list["Call"] = Relationship(back_populates="talkgroup")
