from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlmodel import select
from sqlalchemy import func

from ..db import get_session
from ..db.models.call import Call
from ..db.schemas import (
    CallCreate,
    CallRead,
    CallPatch,
    CallSearch,
    Page,
)
from ..events.publisher import publish_call_update


def create_call(data: CallCreate) -> CallRead:
    """
    Create a new Call row from validated CallCreate data.

    This is used by ingestion/Celery and also (optionally) by API endpoints
    that ingest uploaded recordings.
    """
    with get_session() as session:
        db_call = Call(**data.model_dump())
        session.add(db_call)
        session.flush()  # populate db_call.id
        session.commit()

        # Broadcast to any live subscribers (SSE, websockets, etc.)
        publish_call_update(db_call)

        return CallRead.model_validate(db_call)


def get_call(call_id: int) -> CallRead:
    """Fetch a single Call by primary key and return as CallRead."""
    with get_session() as session:
        result = session.exec(
            select(Call).where(Call.id == call_id)
        ).one()
        return CallRead.model_validate(result)


def patch_call(
        call_id: int,
        patch: CallPatch,
        reviewer_user_id: Optional[int] = None,
) -> CallRead:
    """
    Apply reviewer updates to a Call (corrected_transcript, needs_review).

    If corrected_transcript is provided we also stamp reviewed_at and
    (optionally) reviewed_by.
    """
    now = datetime.utcnow()

    with get_session() as session:
        db_call = session.exec(
            select(Call).where(Call.id == call_id)
        ).one()

        if patch.corrected_transcript is not None:
            db_call.corrected_transcript = patch.corrected_transcript
            db_call.reviewed_at = now
            if reviewer_user_id is not None:
                db_call.reviewed_by = reviewer_user_id

        if patch.needs_review is not None:
            db_call.needs_review = patch.needs_review

        session.add(db_call)
        session.flush()

        publish_call_update(db_call)

        return CallRead.model_validate(db_call)


def search_calls(params: CallSearch) -> Page:
    """
    Filter/paginate calls for UI or API. Supports:
    - system_id / talkgroup_id / unit_id
    - time range (since/until)
    - confidence thresholds
    - basic pagination (page/per_page)

    NOTE: full-text search against transcript_tsv can be added where
    params.text is set. We'll leave a placeholder for that logic.
    """

    # Build WHERE clauses first so we can reuse them for count() and data query.
    where_clauses = []

    if params.system_id is not None:
        where_clauses.append(Call.system_id == params.system_id)

    if params.talkgroup_id is not None:
        where_clauses.append(Call.talkgroup_id == params.talkgroup_id)

    if params.unit_id is not None:
        where_clauses.append(Call.unit_id == params.unit_id)

    if params.since is not None:
        where_clauses.append(Call.timestamp >= params.since)

    if params.until is not None:
        where_clauses.append(Call.timestamp <= params.until)

    if params.min_confidence is not None:
        where_clauses.append(Call.confidence >= params.min_confidence)

    if params.max_confidence is not None:
        where_clauses.append(Call.confidence <= params.max_confidence)

    # Placeholder for full text search (Postgres to_tsquery / @@):
    # if params.text is not None:
    #     where_clauses.append(textsearch_condition)

    with get_session() as session:
        base_query = select(Call)
        if where_clauses:
            for clause in where_clauses:
                base_query = base_query.where(clause)

        # Count total matching rows
        count_query = select(func.count(Call.id))
        if where_clauses:
            for clause in where_clauses:
                count_query = count_query.where(clause)
        total_count = session.exec(count_query).one()

        # Pagination math
        offset = (params.page - 1) * params.per_page
        data_query = (
            base_query
            .order_by(Call.timestamp.desc())
            .offset(offset)
            .limit(params.per_page)
        )

        rows: List[Call] = list(session.exec(data_query))
        dto_items = [CallRead.model_validate(c) for c in rows]

        return Page(
            items=dto_items,
            total=total_count,
            page=params.page,
            per_page=params.per_page,
        )
