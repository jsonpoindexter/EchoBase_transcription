"""Canonical Redis (or NATS, etc.) channel names."""

CALL_EVENTS = "echobase:call_events"      # new transcription finished
HEARTBEAT   = "echobase:heartbeat"        # worker heartbeat / liveness probe

__all__ = ["CALL_EVENTS", "HEARTBEAT"]