from __future__ import annotations

from celery import Celery
from kombu import Exchange, Queue

from ..config import settings

# ---------------------------------------------------------------------------- #
# Celery application
# ---------------------------------------------------------------------------- #
celery_app = Celery(
    "echobase_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,  # keep task-result backend in same Redis
    include=["EchoBase_transcription.worker.tasks"],
)
celery_app.conf.broker_connection_retry_on_startup = True

# Shared task settings
celery_app.conf.update(
    timezone="UTC",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    worker_prefetch_multiplier=1,  # fair scheduling
    task_send_sent_event=True,  # emit “Task-sent” events
    worker_send_task_events=True,  # emit “started/succeeded” events
    task_default_queue="default",
    task_default_exchange="echobase",
    task_default_routing_key="default",
)

# Fan-out durable queue
default_exchange = Exchange("echobase", type="direct")
celery_app.conf.task_queues = (
    Queue("default", default_exchange, routing_key="default"),
)

# Beat scheduler (for housekeeping)
celery_app.conf.beat_schedule = {
    # "cleanup-temp-every-hour": {
    #     "task": "EchoBase_transcription.worker.tasks.housekeeping.cleanup_temp",
    #     "schedule": 3600,
    # },
    "catchup-unprocessed-every-5min": {
        "task": "EchoBase_transcription.worker.tasks.housekeeping.catch_up_unprocessed",
        "schedule": 300,
    },
}