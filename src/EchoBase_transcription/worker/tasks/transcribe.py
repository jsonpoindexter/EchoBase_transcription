"""Celery task to transcribe a single radio call."""
from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ...worker.celery_app import celery_app
from ...config import settings
from ...services.whisper import segment_confidence
from ...db.schemas import CallCreate, RadioUnitCreate, TalkGroupCreate
from ...services.call_service import create_call
from ...services.radio_unit_service import get_or_create_radio_unit
from ...services.talkgroup_service import get_or_create_talkgroup

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
        timestamp: datetime,
        tg_number: Optional[int] = None,
        unit_id: Optional[int] = None,
        system_id: int = 1,  # TODO
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

    # Collapse segments into a single transcript string
    text = " ".join(s.text.strip() for s in segments if s.text.strip())

    # Confidence scoring
    confidences = [segment_confidence(segment) for segment in segments]
    overall_confidence = (
        sum(confidences) / len(confidences) if confidences else None
    )

    # Heuristic review gate
    needs_review = (
            overall_confidence is not None and overall_confidence < -1.0
    )

    # ------------------- 2. Ensure related rows exist ---------------------- #
    # Upsert / resolve RadioUnit (per system_id + unit_id)
    radio_unit_db_id: Optional[int] = None
    if unit_id is not None:
        ru_dto = get_or_create_radio_unit(
            RadioUnitCreate(
                system_id=system_id,
                unit_id=unit_id,
                alias=None,
            )
        )
        radio_unit_db_id = ru_dto.id

    # Upsert / resolve TalkGroup (per system_id + tg_number)
    talkgroup_db_id: Optional[int] = None
    if tg_number is not None:
        tg_dto = get_or_create_talkgroup(
            TalkGroupCreate(
                system_id=system_id,
                tg_number=tg_number,
                alias=None,
                whisper_prompt=None,
            )
        )
        talkgroup_db_id = tg_dto.id

    # ------------------- 3. Create Call row via service -------------------- #
    call_dto = create_call(
        CallCreate(
            system_id=system_id,
            talkgroup_id=talkgroup_db_id,
            unit_id=radio_unit_db_id,
            timestamp=timestamp,
            duration=info.duration,
            audio_path=str(audio_fp),
            transcript=text,
            confidence=overall_confidence,
            needs_review=needs_review,
            transcriber=settings.whisper_model_name,
        )
    )

    # `create_call` already publishes the SSE/update event via call_service

    # ------------------- 4. Return summary to caller ----------------------- #
    return {
        "call_id": call_dto.id,
        "text": text,
        "confidence": overall_confidence,
        "needs_review": needs_review,
    }
