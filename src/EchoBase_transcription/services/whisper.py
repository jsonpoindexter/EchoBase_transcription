import math
import os
from pathlib import Path

from ..config import settings


def segment_confidence(seg):
    return math.exp(seg.avg_logprob) * (1 - seg.no_speech_prob)


class ModelLoader:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = cls._load_model()
        return cls._model

    @staticmethod
    def _load_model():
        from faster_whisper import WhisperModel

        # Determine device
        device = settings.whisper_device
        if device == "auto":
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                device = "cpu"

        # Set model cache directory
        cache_dir = os.environ.get("WHISPER_CACHE_DIR", "/models")
        Path(cache_dir).mkdir(parents=True, exist_ok=True)

        print(
            f"Using faster_whisper model: {settings.whisper_model_name} "
            f"on {device} (compute_type={settings.whisper_compute_type})"
        )

        try:
            # First try with local files only
            model = WhisperModel(
                settings.whisper_model_name,
                device=device,
                compute_type=settings.whisper_compute_type,
                download_root=cache_dir,
                local_files_only=True
            )
            print("Model loaded from local cache")
        except Exception as e:
            print(f"Local model not found, attempting download: {e}")
            try:
                # If local fails, try downloading
                model = WhisperModel(
                    settings.whisper_model_name,
                    device=device,
                    compute_type=settings.whisper_compute_type,
                    download_root=cache_dir,
                    local_files_only=False
                )
                print("Model downloaded successfully")
            except Exception as download_error:
                print(f"Download failed: {download_error}")
                raise RuntimeError(f"Could not load model {settings.whisper_model_name}: {download_error}")

        return model
