"""Upload endpoint that queues a Celery transcription task (FastAPI)."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import mutagen
from fastapi import APIRouter, File, UploadFile, HTTPException, status

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