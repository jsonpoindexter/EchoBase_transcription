from __future__ import annotations

from typing import List

from sqlmodel import select

from ..db import get_session
from ..db.models.system import System
from ..db.schemas import SystemCreate, SystemRead


def get_or_create_system(data: SystemCreate) -> SystemRead:
    """
    Return an existing System with the same name, or create a new one.

    We currently treat System.name as the unique identity for a system.
    If a system already exists but the caller provided a new description,
    we'll update that description.
    """
    with get_session() as session:
        existing = session.exec(
            select(System).where(System.name == data.name)
        ).first()

        if existing:
            # Optionally update description if new info was provided.
            if (
                    data.description is not None
                    and data.description != existing.description
            ):
                existing.description = data.description
                session.add(existing)
                session.flush()

            return SystemRead.model_validate(existing)

        # Create a brand new system
        db_system = System(**data.model_dump())
        session.add(db_system)
        session.flush()

        return SystemRead.model_validate(db_system)


def list_systems() -> List[SystemRead]:
    """
    Return all systems, sorted by name.
    """
    with get_session() as session:
        rows = session.exec(select(System).order_by(System.name.asc())).all()
        return [SystemRead.model_validate(s) for s in rows]


def get_system_by_id(system_id: int) -> SystemRead:
    """
    Fetch a single system by primary key.
    """
    with get_session() as session:
        row = session.exec(
            select(System).where(System.id == system_id)
        ).one()
        return SystemRead.model_validate(row)
