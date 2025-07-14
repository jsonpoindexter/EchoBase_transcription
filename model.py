from config import (
    WHISPER_MODEL_NAME,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
)
from faster_whisper import WhisperModel


class ModelLoader:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = cls._load_model()
        return cls._model

    @staticmethod
    def _load_model():
        # Determine device
        device = WHISPER_DEVICE
        if device == "auto":
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                device = "cpu"

        print(
            f"Using faster_whisper model: {WHISPER_MODEL_NAME} "
            f"on {device} (compute_type={WHISPER_COMPUTE_TYPE})"
        )
        model = WhisperModel(
            WHISPER_MODEL_NAME,
            device=device,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
        return model
