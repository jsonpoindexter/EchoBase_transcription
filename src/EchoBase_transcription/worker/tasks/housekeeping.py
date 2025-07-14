"""Periodic maintenance tasks: clean temp dir & catch up missed files."""

from __future__ import annotations

import logging
from datetime import time
from pathlib import Path
from typing import List

from celery import shared_task

from ...config import settings
from ...db import get_session
from ...db.models import Call
from ...worker.tasks.transcribe import transcribe_audio_task

TEMP_DIR = Path("/app/temp")  # same as volume mount in compose
CALL_DIR = Path(settings.call_watch_path or "/app/recordings")
logger = logging.getLogger(__name__)


# @shared_task(name="cleanup_temp")
# def cleanup_temp() -> None:
#     """Delete leftover temp files older than 24h."""
#     for f in TEMP_DIR.glob("**/*"):
#         if f.is_file() and f.stat().st_mtime < (time.time() - 86_400):
#             try:
#                 f.unlink()
#             except Exception as exc:  # noqa: BLE001
#                 logger.warning("Failed to remove temp file %s: %s", f, exc)


@shared_task(name="catch_up_unprocessed")
def catch_up_unprocessed() -> None:
    """Scan recordings dir; enqueue any audio not in DB."""
    audio_files: List[Path] = list(CALL_DIR.rglob("*.wav")) + list(CALL_DIR.rglob("*.mp3"))
    if not audio_files:
        return

    with get_session() as db:
        existing = {
            Path(p) for (p,) in db.query(Call.audio_path).filter(Call.audio_path.in_(map(str, audio_files)))
        }

    for fp in audio_files:
        if fp not in existing:
            transcribe_audio_task.delay(fp.name, str(fp))