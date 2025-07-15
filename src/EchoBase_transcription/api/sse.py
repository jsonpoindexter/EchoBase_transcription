# src/EchoBase_transcription/api/sse.py
"""Utility to turn event objects into Server‑Sent Events responses (FastAPI)."""

from __future__ import annotations

import json
import uuid
import time
from typing import Generator

from fastapi.responses import StreamingResponse

from ..events import subscribe_call_events, CallEvent

HEARTBEAT_INTERVAL = 25  # seconds  (tweak as desired)


def _serialize_event(evt: CallEvent) -> str:
    """Convert CallEvent → JSON string (or any custom format)."""
    return evt.model_dump_json()


def create_call_stream_response() -> StreamingResponse:
    """Flask Response emitting live CallEvent SSE."""
    client_id = uuid.uuid4().hex
    event_iter = subscribe_call_events()

    def _stream() -> Generator[str, None, None]:
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

    return StreamingResponse(_stream(), media_type="text/event-stream")