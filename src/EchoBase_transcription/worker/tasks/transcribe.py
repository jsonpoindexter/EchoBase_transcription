"""Celery task to transcribe a single radio call."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ...db.schemas import CallCreate
from ...worker.celery_app import celery_app
from ...config import settings
from ...db import get_session
from ...events import publish_call_event, CallEvent
from ...services.whisper import segment_confidence
from ...db.models import Call

# from ...services.whisper import make_prompt

# ----------------------- Load Whisper *once* per worker -------------------- #

# Only load the model in the worker process
if __name__ == "__main__" or os.environ.get("CELERY_WORKER_RUNNING") == "1":
    from ...services.whisper import ModelLoader

    whisper_model = ModelLoader.get_model()
else:
    whisper_model = None  # Not loaded in Flask app

@celery_app.task(name="transcribe_audio", bind=True)
def transcribe_audio_task(
    self,  # Celery task instance
    file_name: str,
    file_path: str,
    prompt: Optional[str] = None,
    language: Optional[str] = None,
) -> dict:
    """Transcribe an audio file and persist the Call row."""
    audio_fp = Path(file_path)

    print(f"Transcribing audio file: {audio_fp} with model {settings.whisper_model_name}")

    # ------------------- 1. Run Faster-Whisper ----------------------------- #
    segments, info = whisper_model.transcribe(
        str(audio_fp),
        language=language,
        # initial_prompt=make_prompt(prompt),
    )
    text = " ".join(s.text.strip() for s in segments if s.text.strip())
    confidence = [segment_confidence(segment) for segment in segments]
    overall_confidence = sum(confidence) / len(confidence) if confidence else None
    needs_review = overall_confidence is not None and overall_confidence < -1.0  # tweak threshold

    # ------------------- 2. Persist in DB ---------------------------------- #
    with get_session() as db:
        # Build a Pydantic DTO for validation first …
        payload = CallCreate(
            system_id=1,
            talkgroup_id=1,
            unit_id=1,
            timestamp=datetime.now(),
            duration=info.duration,
            audio_path=str(audio_fp),
            transcript=text,
            confidence=overall_confidence,
            needs_review=needs_review,
            transcriber=settings.whisper_model_name,
        )

        call = Call(**payload.model_dump())  # type: ignore[arg-type]

        db.add(call)
        db.flush()  # assigns call.id

        # ---------------- 3. Publish event for SSE ------------------------- #
        publish_call_event(
            CallEvent(
                call_id=call.id,
                system_id=call.system_id,
                talkgroup_id=call.talkgroup_id,
                unit_id=call.unit_id,
                timestamp=call.timestamp,
                duration=call.duration,
                confidence=call.confidence,
                needs_review=call.needs_review,
                transcript=call.transcript,
                talkgroup_alias=call.talkgroup.alias if call.talkgroup else None,
                system_name=call.system.name,
            )
        )

    return {"call_id": call.id, "text": text}