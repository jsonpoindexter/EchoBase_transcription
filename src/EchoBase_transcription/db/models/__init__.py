"""SQLAlchemy base metadata and public model re‑exports."""

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Project‑wide declarative base class."""
    pass

from .core import System, TalkGroup, RadioUnit, User, Call