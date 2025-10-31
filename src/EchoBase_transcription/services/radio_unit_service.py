from __future__ import annotations

from typing import List, Optional

from sqlmodel import select

from ..db import get_session
from ..db.models.radio_unit import RadioUnit
from ..db.schemas import RadioUnitCreate, RadioUnitRead


def get_or_create_radio_unit(data: RadioUnitCreate) -> RadioUnitRead:
    """
    Look up a radio unit (unique per system_id + unit_id). If it doesn't
    exist, create it. If it exists and caller passed alias, update it.
    """
    with get_session() as session:
        existing = session.exec(
            select(RadioUnit).where(
                RadioUnit.system_id == data.system_id,
                RadioUnit.unit_id == data.unit_id,
            )
        ).first()

        if existing:
            if data.alias is not None and data.alias != existing.alias:
                existing.alias = data.alias
                session.add(existing)
                session.flush()
            return RadioUnitRead.model_validate(existing)

        db_ru = RadioUnit(**data.model_dump())
        session.add(db_ru)
        session.flush()
        return RadioUnitRead.model_validate(db_ru)


def list_radio_units_for_system(system_id: int) -> List[RadioUnitRead]:
    """List known subscriber radios for a system."""
    with get_session() as session:
        rows = session.exec(
            select(RadioUnit)
            .where(RadioUnit.system_id == system_id)
            .order_by(RadioUnit.unit_id.asc())
        ).all()
        return [RadioUnitRead.model_validate(u) for u in rows]
