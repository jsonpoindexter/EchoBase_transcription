from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class UserBase(SQLModel):
    """Shared attributes for User used in create/read/update."""

    name: str
    email: Optional[str] = None
    api_key: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase, table=True):
    """Future‑use: API / UI user."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
