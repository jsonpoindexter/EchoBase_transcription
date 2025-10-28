"""
Public re-export of API DTO schemas.
"""

from .radio_unit import RadioUnitCreate, RadioUnitRead
from .talkgroup import TalkGroupCreate, TalkGroupRead
from .system import SystemCreate, SystemRead
from .call import (
    CallCreate,
    CallRead,
    CallPatch,
    CallSearch,
)
from .base import DTOBase, Page

__all__ = [
    # Shared
    "DTOBase",
    "Page",
    # System
    "SystemCreate",
    "SystemRead",
    # TalkGroup
    "TalkGroupCreate",
    "TalkGroupRead",
    # RadioUnit
    "RadioUnitCreate",
    "RadioUnitRead",
    # Call
    "CallCreate",
    "CallRead",
    "CallPatch",
    "CallSearch",
]
