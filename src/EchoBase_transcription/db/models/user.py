from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column

from sqlalchemy import String, DateTime


class UserBase(SQLModel):
    """Shared attributes for User used in create/read/update."""

    name: str = Field(
        sa_column=Column(String(100), nullable=False)
    )
    email: Optional[str] = Field(
        default=None,
        sa_column=Column(String(255), unique=True),
    )
    api_key: str = Field(
        sa_column=Column(String(64), unique=True, nullable=False)
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class User(UserBase, table=True):
    """Future‑use: API / UI user."""

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
