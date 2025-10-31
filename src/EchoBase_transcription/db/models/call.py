from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .system import System
    from .talkgroup import TalkGroup
    from .radio_unit import RadioUnit
    from .user import User


class CallBase(SQLModel):
    """Shared attributes for Call used in create/read/update."""

    # Core timing
    timestamp: datetime = Field(index=True)
    duration: Optional[float] = None  # seconds of audio

    # File path
    audio_path: str

    # ASR data
    transcript: Optional[str] = None
    corrected_transcript: Optional[str] = None
    confidence: Optional[float] = None
    needs_review: bool = Field(default=False)
    transcriber: Optional[str] = None

    reviewed_at: Optional[datetime] = None


class Call(CallBase, table=True):
    """Database model for a single recorded radio transmission (one PTT)."""

    __tablename__ = "calls"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Foreign keys
    system_id: int = Field(foreign_key="systems.id", index=True)
    talkgroup_id: Optional[int] = Field(default=None, foreign_key="talkgroups.id", index=True)
    unit_id: Optional[int] = Field(default=None, foreign_key="radio_units.id", index=True)
    reviewed_by: Optional[int] = Field(default=None, foreign_key="users.id")

    # Relationships
    system: "System" = Relationship(back_populates="calls")
    talkgroup: Optional["TalkGroup"] = Relationship(back_populates="calls")
    unit: Optional["RadioUnit"] = Relationship(back_populates="calls")
    reviewer: Optional["User"] = Relationship()
