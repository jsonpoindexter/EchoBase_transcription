"""SQLAlchemy base metadata and public model re‑exports."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Project‑wide declarative base class."""
    pass


from .system import System
from .talkgroup import TalkGroup
from .radio_unit import RadioUnit
from .call import Call
from .user import User
