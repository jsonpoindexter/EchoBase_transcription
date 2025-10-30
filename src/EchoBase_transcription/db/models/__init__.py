"""SQLAlchemy base metadata and public model re‑exports."""
from sqlalchemy import MetaData
from sqlmodel import SQLModel


NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Set the global metadata used by SQLModel BEFORE any models import
SQLModel.metadata = MetaData(naming_convention=NAMING_CONVENTION)

from .system import System
from .talkgroup import TalkGroup
from .radio_unit import RadioUnit
from .call import Call
from .user import User

__all__ = [
    "System",
    "TalkGroup",
    "RadioUnit",
    "Call",
    "User",
]
