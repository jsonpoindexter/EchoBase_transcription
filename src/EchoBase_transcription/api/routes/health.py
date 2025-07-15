"""Health‑check endpoint (FastAPI version)."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health", response_model=dict[str, str])
async def health() -> dict[str, str]:
    """Return a simple liveness probe."""
    return {"status": "ok"}