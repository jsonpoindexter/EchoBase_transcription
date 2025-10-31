"""Publish helpers wrapping Redis in a thin layer."""

from __future__ import annotations

from datetime import datetime

import redis
from ..config.settings import settings
from .channels import CALL_EVENTS, HEARTBEAT
from .schemas import CallEvent, Heartbeat
from ..db.models import Call

# Instantiate one Redis connection for publishers
_redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def publish_call_update(call: Call) -> None:
    """Publish a CallEvent to CALL_EVENTS channel."""
    dto = CallEvent(
        call_id=call.id,
        system_id=call.system_id,
        talkgroup_id=call.talkgroup_id,
        unit_id=(getattr(call.unit, "unit_id", None) if call.unit_id else None),  # use radio_units.unit_id
        timestamp=call.timestamp,
        duration=call.duration,
        transcript=call.transcript,
        corrected_transcript=call.corrected_transcript,
        confidence=call.confidence,
        needs_review=call.needs_review,
        transcriber=call.transcriber,
        reviewed_at=call.reviewed_at,
        reviewed_by=call.reviewed_by,
        talkgroup_alias=(getattr(call.talkgroup, "alias", None) if call.talkgroup_id else None),
        unit_alias=(getattr(call.unit, "alias", None) if call.unit_id else None),
    )
    _redis_client.publish(CALL_EVENTS, dto.model_dump_json())


def publish_heartbeat(worker_id: str) -> None:
    """Publish a Heartbeat message (called by a Celery beat job)."""
    hb = Heartbeat(worker_id=worker_id, ts=datetime.now())
    _redis_client.publish(HEARTBEAT, hb.model_dump_json())
