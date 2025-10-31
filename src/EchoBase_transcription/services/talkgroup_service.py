from __future__ import annotations

from typing import List

from sqlmodel import select

from ..db import get_session
from ..db.models.talkgroup import TalkGroup
from ..db.schemas import TalkGroupCreate, TalkGroupRead


def get_or_create_talkgroup(data: TalkGroupCreate) -> TalkGroupRead:
    """
    Ensure we have a TalkGroup row for (system_id, tg_number).

    If it already exists:
      - Optionally update alias and whisper_prompt if the caller passed new values.
      - Return the updated row as TalkGroupRead.

    If it doesn't exist:
      - Create it using the provided TalkGroupCreate data.
      - Return TalkGroupRead for the new row.

    This is used by ingestion (Celery) and can also be used by API routes.
    """
    with get_session() as session:
        existing = session.exec(
            select(TalkGroup).where(
                TalkGroup.system_id == data.system_id,
                TalkGroup.tg_number == data.tg_number,
            )
        ).first()

        if existing:
            changed = False

            # Update alias if we were given a new alias
            if data.alias is not None and data.alias != existing.alias:
                existing.alias = data.alias
                changed = True

            # Update whisper_prompt similarly
            if (
                    data.whisper_prompt is not None
                    and data.whisper_prompt != existing.whisper_prompt
            ):
                existing.whisper_prompt = data.whisper_prompt
                changed = True

            if changed:
                session.add(existing)
                session.flush()

            return TalkGroupRead.model_validate(existing)

        # Not found -> create new TalkGroup
        db_tg = TalkGroup(**data.model_dump())
        session.add(db_tg)
        session.flush()

        return TalkGroupRead.model_validate(db_tg)


def list_talkgroups_for_system(system_id: int) -> List[TalkGroupRead]:
    """
    Return all TalkGroups for a given system_id, sorted by tg_number.
    This is convenient for UI dropdowns / browsing.
    """
    with get_session() as session:
        rows = session.exec(
            select(TalkGroup)
            .where(TalkGroup.system_id == system_id)
            .order_by(TalkGroup.tg_number.asc())
        ).all()

        return [TalkGroupRead.model_validate(tg) for tg in rows]
