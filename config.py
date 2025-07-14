import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

FLASK_API_KEY = os.getenv("FLASK_API_KEY")
print(f"FLASK_API_KEY: {FLASK_API_KEY}")
FLASK_PORT = os.getenv("FLASK_PORT")
print(f"FLASK_PORT: {FLASK_PORT}")
FLASK_BASE_PATH = os.getenv("FLASK_BASE_PATH")
print(f"FLASK_BASE_PATH: {FLASK_BASE_PATH}")
FLASK_RATE_LIMIT = os.getenv("FLASK_RATE_LIMIT")
print(f"FLASK_RATE_LIMIT: {FLASK_RATE_LIMIT}")

REDIS_URL = os.getenv("REDIS_URL")
print(f"REDIS_URL: {REDIS_URL}")

WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME")
print(f"WHISPER_MODEL_NAME: {WHISPER_MODEL_NAME}")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE")
print(f"WHISPER_LANGUAGE: {WHISPER_LANGUAGE}")
WHISPER_INITIAL_PROMPT = os.getenv("WHISPER_INITIAL_PROMPT", "").strip()
print(f"WHISPER_INITIAL_PROMPT: {WHISPER_INITIAL_PROMPT}")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "auto").lower()
print(f"WHISPER_DEVICE: {WHISPER_DEVICE}")
WHISPER_COMPUTE_TYPE = os.getenv(
    "WHISPER_COMPUTE_TYPE",
    "float16" if WHISPER_DEVICE in ("cuda", "auto") else "int8"
).lower()
print(f"WHISPER_COMPUTE_TYPE: {WHISPER_COMPUTE_TYPE}")

CALL_WATCH_PATH = os.getenv("CALL_WATCH_PATH")
print(f"CALL_WATCH_PATH: {CALL_WATCH_PATH}")

# -------------------------------------------------
#  Flask configuration objects
# -------------------------------------------------
class BaseConfig:
    # Environment‑driven secrets and knobs
    FLASK_API_KEY = FLASK_API_KEY
    FLASK_PORT = FLASK_PORT
    FLASK_BASE_PATH = FLASK_BASE_PATH
    FLASK_RATE_LIMIT = FLASK_RATE_LIMIT
    REDIS_URL = REDIS_URL
    WHISPER_MODEL_NAME = WHISPER_MODEL_NAME
    WHISPER_LANGUAGE = WHISPER_LANGUAGE
    WHISPER_INITIAL_PROMPT = WHISPER_INITIAL_PROMPT
    WHISPER_COMPUTE_TYPE = WHISPER_COMPUTE_TYPE
    WHISPER_DEVICE = WHISPER_DEVICE
    CALL_WATCH_PATH = CALL_WATCH_PATH

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    CORS_ALLOW_ALL_ORIGINS = True

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "http"