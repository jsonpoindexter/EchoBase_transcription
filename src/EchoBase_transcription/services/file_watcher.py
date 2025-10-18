import threading
import time
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver as Observer

from ..config import settings
from ..worker.tasks.transcribe import transcribe_audio_task


class FileWatcher(FileSystemEventHandler):
    def __init__(self):
        super().__init__()

    def on_created(self, event):
        self._maybe_transcribe(event)

    def on_moved(self, event):
        self._maybe_transcribe(event, moved=True)

    def _maybe_transcribe(self, event, *, moved=False):
        if event.is_directory:
            return  # skip folders
        if not event.src_path.lower().endswith((".wav", ".mp3")):
            return
        print(f"{'Moved' if moved else 'Created'}: {event.src_path}", flush=True)
        transcribe_audio_task.delay(
            file_name=event.src_path.split("/")[-1],
            file_path=event.src_path,
            prompt=settings.whisper_initial_prompt,
            language=settings.whisper_language,
        )


def start_file_watcher(path: str) -> threading.Thread:
    """Start the observer in a daemon thread and return the thread object."""
    print(f"Starting file watcher on: {path}", flush=True)
    observer = Observer()
    observer.schedule(FileWatcher(), path, recursive=True)
    observer.start()

    def _keep_alive():
        try:
            while observer.is_alive():
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()

    t = threading.Thread(target=_keep_alive, daemon=True)
    t.start()
    return t
