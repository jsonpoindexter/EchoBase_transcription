"""FastAPI application factory and instance for EchoBase Transcription."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from ..config.settings import settings
from ..services.file_watcher import start_file_watcher


def add_base_path(route: str) -> str:
    """Prefix each route with settings.base_path ('' in dev)."""
    return f"/{settings.base_path.strip('/')}{route}" if settings.base_path else route


def create_app() -> FastAPI:  # noqa: D401
    """Return a configured FastAPI app."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):  # noqa: D401
        """Startup/Shutdown context for FastAPI 0.110+."""
        # if settings.call_watch_path:
        #     if not (settings.env == "development" and os.environ.get("RUN_MAIN") == "true"):
        #         # avoid double-start when uvicorn reloads
        #         start_file_watcher(settings.call_watch_path)
        yield
        # (optional) add any shutdown cleanup here

    app = FastAPI(
        title="EchoBase Transcription API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        root_path=f"/{settings.base_path.strip('/')}" if settings.base_path else "",
        lifespan=lifespan,
    )

    # ----------------------------- Middleware ----------------------------- #
    app.add_middleware(GZipMiddleware, minimum_size=1_000)

    # ------------------------------- Static ------------------------------- #
    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # ------------------------------ Routers ------------------------------ #
    from .routes.health import router as health_router  # FastAPI routers
    from .routes.transcribe import router as transcribe_router
    from .routes.stream import router as stream_router
    from .routes.systems import router as system_router

    app.include_router(health_router, prefix=add_base_path(""))
    app.include_router(transcribe_router, prefix=add_base_path(""))
    app.include_router(stream_router, prefix=add_base_path(""))
    app.include_router(system_router, prefix=add_base_path(""))

    # -------------------------- Exception handler ------------------------- #
    @app.exception_handler(Exception)
    async def _unhandled(request, exc):  # noqa: ANN001
        """Catch-all: log & return JSON 500."""
        import logging

        logging.getLogger("uvicorn.error").exception("Unhandled exception: %s", exc)
        return JSONResponse({"error": str(exc)}, status_code=500)

    return app


app = create_app()
