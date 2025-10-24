"""Upload endpoint that queues a Celery transcription task (FastAPI)."""

from __future__ import annotations

import mutagen
from fastapi import APIRouter, File, UploadFile, HTTPException, status
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel

from ...config.settings import settings
from ...worker.tasks.transcribe import transcribe_audio_task

router = APIRouter()

TEMP_DIR = Path(settings.temp_audio_path)
TEMP_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/transcribe", status_code=status.HTTP_202_ACCEPTED)
async def handle_transcribe_audio(file: UploadFile = File(...)) -> dict[str, str]:
    """Accept a WAV/MP3 file, save to disk, enqueue Celery task, return task ID."""
    file_path = TEMP_DIR / f"{uuid4()}_{file.filename}"
    file_path.write_bytes(await file.read())

    if file_path.suffix.lower() not in {".wav", ".mp3"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    try:
        if mutagen.File(file_path) is None:
            raise ValueError
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid audio file")

    task = transcribe_audio_task.delay(
        file.filename,
        str(file_path),
        prompt=settings.whisper_initial_prompt,
        language=settings.whisper_language,
    )

    return {"message": "Transcription started", "taskId": task.id}


class InternalTranscribeRequest(BaseModel):
    file_name: str
    timestamp: str
    site: str | None = None
    source_id: str
    destination_id: str


@router.post("/internal/transcribe", status_code=status.HTTP_202_ACCEPTED)
async def handle_internal_transcribe_audio(
        request: InternalTranscribeRequest) -> dict[str, str]:
    """Accept a WAV/MP3 file name and reference the binded SDRTrunk recording diretory (CALL_WATCH_PATH), enqueue Celery task, return task ID."""

    print(f"Received internal transcribe request: {request}")
    file_name = request.file_name
    timestamp = request.timestamp
    site = request.site
    source_id = request.source_id
    destination_id = request.destination_id

    print(f"Internal transcribe request for file: {file_name}")

    if Path(file_name).suffix.lower() not in {".wav", ".mp3"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Resolve full path and validate existence/content
    full_path = Path(settings.call_watch_path) / file_name
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        if mutagen.File(str(full_path)) is None:
            raise ValueError
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid audio file")

    task = transcribe_audio_task.delay(
        file_name,
        file_path=str(full_path),
        prompt=settings.whisper_initial_prompt,
        language=settings.whisper_language,
        timestamp=timestamp,
        tg_number=int(destination_id) if destination_id and destination_id.isdigit() else None,
        unit_id=int(source_id) if source_id and source_id.isdigit() else None
    )

    return {"message": "Transcription started", "taskId": task.id}
