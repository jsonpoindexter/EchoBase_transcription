import json
import redis
from config import REDIS_URL

redis_client = redis.Redis.from_url(REDIS_URL)


def publish_event(event_type, data):
    """Publish event to Redis channel"""
    payload = {
        "type": event_type,
        "data": data
    }
    redis_client.publish('transcription_events', json.dumps(payload))
