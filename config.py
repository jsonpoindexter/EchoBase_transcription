# config.py
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FLASK_API_KEY = os.getenv("FLASK_API_KEY")
FLASK_PORT = os.getenv("FLASK_PORT")
FLASK_BASE_PATH = os.getenv("FLASK_BASE_PATH")
FLASK_RATE_LIMIT = os.getenv("FLASK_RATE_LIMIT")
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE")
WHISPER_INITIAL_PROMPT = os.getenv("WHISPER_INITIAL_PROMPT", "").strip()
