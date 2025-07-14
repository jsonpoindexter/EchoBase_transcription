"""Utility to subscribe to channels and yield typed events."""

from __future__ import annotations

import json
from typing import Generator, Type

import redis

from ..config.settings import settings
from .channels import CALL_EVENTS, HEARTBEAT
from .schemas import CallEvent, Heartbeat

_channel_to_schema: dict[str, Type] = {
    CALL_EVENTS: CallEvent,
    HEARTBEAT: Heartbeat,
}

# One connection per listener (Redis pubsub objects aren’t thread-safe)
def subscribe(*channels: str) -> Generator[object, None, None]:
    """Yield parsed Pydantic objects as they arrive on the given channels."""
    r = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(*channels)

    for message in pubsub.listen():
        if message["type"] != "message":
            continue
        chan = message["channel"]
        schema_cls = _channel_to_schema.get(chan)
        if schema_cls is None:
            # Unknown channel – just yield raw JSON
            yield json.loads(message["data"])
            continue
        try:
            yield schema_cls.parse_raw(message["data"])
        except Exception as exc:  # noqa: BLE001
            # In production, log or capture to Sentry
            print(f"Malformed event on {chan}: {exc}")


def subscribe_call_events():
    """Shortcut for the most common need: live call updates."""
    yield from subscribe(CALL_EVENTS)