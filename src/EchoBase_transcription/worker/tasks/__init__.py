"""Auto-import task modules so Celery sees them."""
from . import transcribe  # noqa: F401
from . import housekeeping  # noqa: F401