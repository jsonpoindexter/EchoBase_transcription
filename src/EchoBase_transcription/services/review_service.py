from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import select

from ..db import get_session
from ..db.models.call import Call
from ..db.schemas import CallRead
from ..events.publisher import publish_call_update


def apply_human_review(
        call_id: int,
        corrected_transcript: Optional[str],
        needs_review: Optional[bool],
        reviewer_user_id: Optional[int],
) -> CallRead:
    """
    High-level wrapper specifically for the human review flow.

    - Stores corrected_transcript (if provided)
    - Marks needs_review (if provided)
    - Stamps reviewed_by / reviewed_at if corrected_transcript was set
    - Publishes an update event
    """
    now = datetime.utcnow()

    with get_session() as session:
        db_call = session.exec(
            select(Call).where(Call.id == call_id)
        ).one()

        changed = False

        if corrected_transcript is not None:
            db_call.corrected_transcript = corrected_transcript
            db_call.reviewed_at = now
            if reviewer_user_id is not None:
                db_call.reviewed_by = reviewer_user_id
            changed = True

        if needs_review is not None:
            db_call.needs_review = needs_review
            changed = True

        if changed:
            session.add(db_call)
            session.flush()
            publish_call_update(db_call)

        return CallRead.model_validate(db_call)
