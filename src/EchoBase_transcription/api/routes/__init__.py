"""Re-export FastAPI routers for easy import elsewhere."""

from .health import router as health_router
from .transcribe import router as transcribe_router
from .stream import router as stream_router

__all__ = [
    "health_router",
    "transcribe_router",
    "stream_router",
]