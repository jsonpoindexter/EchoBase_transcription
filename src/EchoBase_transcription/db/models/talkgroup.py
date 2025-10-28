from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base

if TYPE_CHECKING:
    # These imports are ONLY for the type checker / IDE.
    # They do NOT run at runtime, so they do NOT create a cycle.
    from .system import System
    from .call import Call


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
