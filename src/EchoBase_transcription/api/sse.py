# src/EchoBase_transcription/api/sse.py
"""Utility to turn event objects into Server-Sent Events responses."""

from __future__ import annotations

import json
import uuid
from typing import Generator

from flask import Response, stream_with_context

from ..events import subscribe_call_events, CallEvent

HEARTBEAT_INTERVAL = 25  # seconds  (tweak as desired)


def _serialize_event(evt: CallEvent) -> str:
    """Convert CallEvent → JSON string (or any custom format)."""
    return evt.model_dump_json()


def create_call_stream_response() -> Response:
    """Flask Response emitting live CallEvent SSE."""
    client_id = uuid.uuid4().hex
    event_iter = subscribe_call_events()

    def _stream() -> Generator[str, None, None]:
        import time

        last_heartbeat = time.time()
        for evt in event_iter:
            # Filter here if you need per-request scoping
            yield f"id: {evt.call_id}\n"
            yield f"event: call\n"
            yield f"data: {_serialize_event(evt)}\n\n"

            # Heartbeat comments keep proxies from timing out idle streams
            if time.time() - last_heartbeat > HEARTBEAT_INTERVAL:
                yield ": heartbeat\n\n"
                last_heartbeat = time.time()

    return Response(stream_with_context(_stream()), mimetype="text/event-stream")