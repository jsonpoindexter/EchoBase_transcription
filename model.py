import os

import torch
import whisper

from config import WHISPER_MODEL_NAME


class ModelLoader:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            cls._model = cls._load_model()
        return cls._model

    @staticmethod
    def _load_model():
        print(f"CUDA available: {torch.cuda.is_available()}")
        print(f"Available whisper models: {whisper.available_models()}")
        print(f"Using model: {WHISPER_MODEL_NAME}")

        # Make sure WHISPER_MODEL_NAME is available
        if WHISPER_MODEL_NAME not in whisper.available_models():
            raise ValueError(f"WHISPER_MODEL_NAME {WHISPER_MODEL_NAME} not available")

        model_path = f"/models/{WHISPER_MODEL_NAME}"
        if not os.path.exists(model_path):
            torch.cuda.init()
            model = whisper.load_model(WHISPER_MODEL_NAME)
            torch.save(model, model_path)
        else:
            model = torch.load(model_path, weights_only=False)
        return model
