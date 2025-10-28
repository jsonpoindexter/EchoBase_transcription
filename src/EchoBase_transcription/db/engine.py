"""SQLAlchemy engine and session factory for the radio_transcript project."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session

from ..config import settings

# --------------------------------------------------------------------------- #
# Engine & Session
# --------------------------------------------------------------------------- #
engine: Engine = create_engine(
    settings.database_url,
    future=True,  # 2.0 style
    pool_pre_ping=True,  # Detect stale connections
    echo=settings.sqlalchemy_echo,
)

# Thread‑local scoped session; suitable for Flask and Celery workers alike.
SessionLocal = scoped_session(
    sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
)

__all__ = ["engine", "SessionLocal"]
