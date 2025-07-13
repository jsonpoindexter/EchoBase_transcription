import json
import redis
from flask import Response, stream_with_context
from config import REDIS_URL

# Connect to Redis
redis_client = redis.Redis.from_url(REDIS_URL)


def event_stream(client_id):
    """Generate SSE stream from Redis subscription"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe('transcription_events')

    # Send initial connection event
    yield "event: connected\ndata: {}\n\n"

    try:
        for message in pubsub.listen():
            if message['type'] == 'message':
                yield f"data: {message['data'].decode()}\n\n"
    finally:
        pubsub.unsubscribe('transcription_events')


def create_stream_response(client_id):
    """Create Flask SSE response"""
    return Response(
        stream_with_context(event_stream(client_id)),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
