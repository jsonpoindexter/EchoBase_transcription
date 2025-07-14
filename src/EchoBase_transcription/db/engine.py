"""SQLAlchemy engine and session factory for the radio_transcript project."""

from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, scoped_session

from ..config import settings

# If you set SQLALCHEMY_ECHO=1 in the environment you’ll get SQL debug logs.
ECHO_SQL: bool = bool(int(os.getenv("SQLALCHEMY_ECHO", "0")))

# --------------------------------------------------------------------------- #
# Engine & Session
# --------------------------------------------------------------------------- #
engine: Engine = create_engine(
    settings.database_url,
    future=True,          # 2.0 style
    pool_pre_ping=True,   # Detect stale connections
    echo=ECHO_SQL,
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