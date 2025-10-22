"""Re-export FastAPI routers for easy import elsewhere."""

from .health import router as health_router
from .transcribe import router as transcribe_router
from .stream import router as stream_router
from .systems import router as system_router
from .talkgroups import router as talkgroup_router
from .internal.ingest import router as ingest_router

__all__ = [
    "health_router",
    "transcribe_router",
    "stream_router",
    "system_router",
    "talkgroup_router",
    "ingest_router",
]
