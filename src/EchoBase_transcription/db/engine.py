from __future__ import annotations

from sqlmodel import create_engine, Session
from sqlalchemy.orm import scoped_session, sessionmaker

from ..config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.sqlalchemy_echo,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = scoped_session(
    sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=Session,
    )
)
