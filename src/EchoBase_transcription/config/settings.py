"""Centralised application settings parsed from environment variables.

    Uses **Pydantic** so we get type‑safety, default values, and `dotenv` support.
    Access as a singleton:

        from EchoBase_transcription.config import settings
    """

from __future__ import annotations

from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --------------------------------------------------------------------- #
    # Flask / API
    # --------------------------------------------------------------------- #
    api_key: str = Field(..., validation_alias="FLASK_API_KEY")
    API_PORT: int = Field(3000, validation_alias="API_PORT")
    base_path: str = Field("", validation_alias="FLASK_BASE_PATH")
    rate_limit: str = Field("60/minute", validation_alias="FLASK_RATE_LIMIT")

    # --------------------------------------------------------------------- #
    # Redis & Celery
    # --------------------------------------------------------------------- #
    redis_url: str = Field("redis://redis:6379/0", validation_alias="REDIS_URL")

    # --------------------------------------------------------------------- #
    # Whisper
    # --------------------------------------------------------------------- #
    whisper_model_name: str = Field("base.en", validation_alias="WHISPER_MODEL_NAME")
    whisper_language: str = Field("en", validation_alias="WHISPER_LANGUAGE")
    whisper_initial_prompt: str = Field("", validation_alias="WHISPER_INITIAL_PROMPT")
    whisper_device: str = Field("auto", validation_alias="WHISPER_DEVICE")
    whisper_compute_type: Optional[str] = Field(None, validation_alias="WHISPER_COMPUTE_TYPE")

    # --------------------------------------------------------------------- #
    # Files & paths
    # --------------------------------------------------------------------- #
    call_watch_path: Optional[str] = Field(None, validation_alias="CALL_WATCH_PATH")
    temp_audio_path: str = Field("/tmp/audio", validation_alias="TEMP_AUDIO_PATH")

    # --------------------------------------------------------------------- #
    # Database
    # --------------------------------------------------------------------- #
    database_url: str = Field(
        "postgresql+psycopg2://user:password@db/echobase",
        validation_alias="DATABASE_URL",
    )
    sqlalchemy_echo: bool = Field(
        False, validation_alias="SQLALCHEMY_ECHO"
    )  # SQLAlchemy debug logging

    # --------------------------------------------------------------------- #
    # Misc
    # --------------------------------------------------------------------- #
    env: str = Field("development", validation_alias="ENVIRONMENT")
    sql_echo: bool = Field(False, validation_alias="SQLALCHEMY_ECHO")


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"

    @model_validator(mode="before")
    def _derive_whisper_compute(cls, values):
        dev = values.get("whisper_device", "auto").lower()
        values.setdefault(
            "whisper_compute_type",
            "float16" if dev in {"cuda", "auto"} else "int8",
        )
        return values

# Instantiate a singleton for the whole app to import
settings = Settings()
