from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool, create_engine
from sqlmodel import SQLModel

# --- Make sure `src` is on sys.path so we can import your package ---
# This assumes repo structure: <repo> / src / EchoBase_transcription / ...
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(REPO_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# --- Import your settings and models so tables register on SQLModel.metadata ---
from src.EchoBase_transcription.config.settings import settings  # adjust attr name if needed
# Import modules to register tables (do NOT remove); explicit is safest.
from src.EchoBase_transcription.db.models import (  # noqa: F401
    system,
    talkgroup,
    radio_unit,
    call,
    user,
)

# Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---- Resolve database URL ----
# Prefer env var (e.g., CI/CD), else your app settings
db_url = os.getenv("DATABASE_URL") or getattr(settings, "database_url", None)
if not db_url:
    raise RuntimeError(
        "DATABASE_URL is not set and settings.database_url is empty. "
        "Set env var DATABASE_URL or configure it in EchoBase_transcription.config.settings."
    )

# Target metadata for 'autogenerate'
target_metadata = SQLModel.metadata

# Autogenerate tuning
COMPARE_TYPES = True
COMPARE_SERVER_DEFAULT = True


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=COMPARE_TYPES,
        compare_server_default=COMPARE_SERVER_DEFAULT,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=False,  # set True only if you need batch mode (e.g., SQLite)
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    engine = create_engine(db_url, poolclass=pool.NullPool, future=True)
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=COMPARE_TYPES,
            compare_server_default=COMPARE_SERVER_DEFAULT,
            render_as_batch=False,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
