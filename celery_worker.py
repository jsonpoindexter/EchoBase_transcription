import os
from celery import Celery

transcription_worker = Celery("transcriptionTasks", broker="redis://redis:6379", backend="redis://redis:6379")

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
        end_time = time.time()
        transcribe_time = end_time - start_time
        print(f"Transcription completed for {file_name} in {transcribe_time} seconds")
        print(info)
        text = "".join([segment.text for segment in segments])
        return {
            "file_name": file_name,
            "text": text,
            "language": info.language,
            "duration": info.duration,
            "transcribe_time": transcribe_time
        }
    except Exception as e:
        return {"error": str(e), "type": type(e).__name__}


if __name__ == "__main__" or os.environ.get("CELERY_WORKER_RUNNING") == "1":
    transcription_worker.task(transcribe_audio)

if __name__ == "__main__":
    transcription_worker.worker_main()
