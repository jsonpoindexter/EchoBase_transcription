"""Expose a singleton settings object across the application."""
from .settings import Settings, settings

__all__: list[str] = ["Settings", "settings"]