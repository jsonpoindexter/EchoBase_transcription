"""Database utilities and public re‑exports for the radio_transcript package.

This sub‑package centralises all DB‑related helpers so that callers can simply:

    from radio_transcript.db import SessionLocal, get_session, init_db

without importing SQLAlchemy internals everywhere.
"""

from contextlib import contextmanager
from typing import Generator

from .engine import engine, SessionLocal
from sqlmodel import SQLModel


def init_db() -> None:
    """Create all tables if they do not exist (idempotent).

    In production environments, prefer Alembic migrations.
    This helper is handy for unit tests or one‑off scripts.
    """
    SQLModel.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator:
    """Provide a transactional scope around a series of operations.

    Usage:
        with get_session() as db:
            db.add(obj)
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
