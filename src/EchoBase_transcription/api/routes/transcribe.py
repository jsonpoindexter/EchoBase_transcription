from pathlib import Path
from uuid import uuid4

import mutagen
from flask import Blueprint, jsonify, request

from ...worker.tasks.transcribe import transcribe_audio_task
from ...config.settings import settings

bp = Blueprint("transcribe", __name__)

TEMP_DIR = Path(settings.temp_audio_path)
TEMP_DIR.mkdir(parents=True, exist_ok=True)


@bp.route("/transcribe", methods=["POST"])
def handle_transcribe_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    file_path = TEMP_DIR / f"{uuid4()}_{file.filename}"
    file.save(file_path)

    if file_path.suffix.lower() not in (".wav", ".mp3"):
        return jsonify({"error": "Unsupported file type"}), 400
    try:
        if mutagen.File(file_path) is None:
            raise ValueError
    except Exception:
        return jsonify({"error": "Invalid audio file"}), 400

    print(f"Received file: {file.filename}, saved to {file_path}")
    task = transcribe_audio_task.delay(  # Celery task
        file.filename,
        str(file_path),
        prompt=settings.whisper_initial_prompt,
        language=settings.whisper_language,
    )
    return jsonify({"message": "Transcription started", "taskId": task.id}), 202