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
    dto = CallEvent.model_validate(call, from_attributes=True)
    _redis_client.publish(CALL_EVENTS, dto.model_dump_json())


def publish_heartbeat(worker_id: str) -> None:
    """Publish a Heartbeat message (called by a Celery beat job)."""
    hb = Heartbeat(worker_id=worker_id, ts=datetime.now())
    _redis_client.publish(HEARTBEAT, hb.model_dump_json())
