"""Server‑Sent Events endpoint for live transcription updates (FastAPI)."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from ..sse import create_call_stream_response

router = APIRouter()


@router.get("/transcription/events", response_class=StreamingResponse)
async def transcription_events() -> StreamingResponse:
    """
    Return an SSE stream of CallEvent objects.
    """
    return create_call_stream_response()
