from config import WHISPER_MODEL_NAME
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
        print(f"Using faster_whisper model: {WHISPER_MODEL_NAME}")
        # You can set device="cuda" if CUDA is available, else "cpu"
        # model = WhisperModel(WHISPER_MODEL_NAME, device="cuda" if WhisperModel.is_cuda_available() else "cpu")
        model = WhisperModel(WHISPER_MODEL_NAME, device="cuda", compute_type="float16")
        return model
