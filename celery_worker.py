import os
from dataclasses import asdict
from celery import Celery
from config import REDIS_URL
from models.utils import segment_confidence
from sse_publisher import publish_event

transcription_worker = Celery("transcriptionTasks", broker=REDIS_URL, backend=REDIS_URL)

# Only load the model in the worker process
if __name__ == "__main__" or os.environ.get("CELERY_WORKER_RUNNING") == "1":
    from model import ModelLoader

    model = ModelLoader.get_model()
else:
    model = None  # Not loaded in Flask app


@transcription_worker.task
def transcribe_audio(
        file_name,
        file_path,
        prompt,
        language,
):
    import time
    if model is None:
        # Defensive: should never happen in worker
        return {"error": "Model not loaded", "type": "RuntimeError"}
    try:
        print(f"Metadata:  {os.stat(file_path)}")
        transcribe_args = {'audio': file_path, 'language': language, 'initial_prompt': prompt}
        start_time = time.time()
        segments, info = model.transcribe(**transcribe_args)
        segments = list(segments)
        end_time = time.time()
        processing_time_seconds = end_time - start_time
        print(f"Transcription completed for {file_name} in {processing_time_seconds} seconds")
        print(segments)
        print(info)

        text = "".join([segment.text for segment in segments])
        result = {
            "file_name": file_name,
            "text": text,
            "language": info.language,
            "duration": info.duration,
            "processing_time_seconds": processing_time_seconds,
            "segments": [asdict(s) for s in segments],
            "confidence": [segment_confidence(segment) for segment in segments],
        }
        publish_event(event_type="transcription_completed", data=result)
        return result
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


if __name__ == "__main__" or os.environ.get("CELERY_WORKER_RUNNING") == "1":
    transcription_worker.task(transcribe_audio)

if __name__ == "__main__":
    transcription_worker.worker_main()
