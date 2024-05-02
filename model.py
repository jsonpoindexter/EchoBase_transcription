import os

import torch
import whisper

from config import WHISPER_MODEL_NAME


def load_model():
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
        model = torch.load(model_path)
    return model
