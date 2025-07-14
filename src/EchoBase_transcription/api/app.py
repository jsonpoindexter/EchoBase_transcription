from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import HTTPException, ClientDisconnected

from ..config.settings import settings
from ..services.file_watcher import start_file_watcher

# ---- Swagger / OpenAPI ----
from flask_swagger_generator.generators import Generator
from flask_swagger_generator.utils import SwaggerVersion
from flask_swagger_ui import get_swaggerui_blueprint

# create the generator once
swagger_gen = Generator.of(SwaggerVersion.VERSION_THREE)
current_directory = os.getcwd()

def add_base_path(route: str) -> str:
    """Prefix every route with settings.base_path ('' in dev)."""
    if not settings.base_path:
        return route
    return f"/{settings.base_path}{route}"


def create_app() -> Flask:
    """Application factory – importable by gunicorn / Celery tests."""
    app = Flask(__name__)
    app.config.update(
        ENV=settings.env,
        DEBUG=True,
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=100 * 1024 * 1024,  # 100 MB upload cap
    )

    # ------------------------------- Extensions ---------------------------- #
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # ------------------------------ Blueprints ----------------------------- #
    from .routes.health import bp as health_bp
    from .routes.transcribe import bp as transcribe_bp
    from .routes.stream import bp as stream_bp

    app.register_blueprint(health_bp, url_prefix=add_base_path(""))
    app.register_blueprint(transcribe_bp, url_prefix=add_base_path(""))
    app.register_blueprint(stream_bp, url_prefix=add_base_path(""))

    # -------------------------- Swagger generation ------------------------- #
    static_dir = Path(app.instance_path).parent / "static"
    swagger_destination_path = static_dir / "swagger.yaml"
    os.makedirs(static_dir, exist_ok=True)
    swagger_gen.generate_swagger(app, destination_path=str(swagger_destination_path))

    app.static_folder = str(static_dir)
    app.static_url_path = "/static"

    swagger_ui = get_swaggerui_blueprint(
        "/docs",
        "/static/swagger.yaml",  # URL path to the swagger file
        config={"app_name": "EchoBase API Docs", "docExpansion": "none"},
    )
    app.register_blueprint(swagger_ui, url_prefix="/docs")

    # ------------------------- File-watcher startup ------------------------ #
    if settings.call_watch_path and (
        not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    ):
        app.logger.info(f"Watching for new audio files in {settings.call_watch_path}")
        start_file_watcher(settings.call_watch_path)

    # -------------------------- Error handlers ----------------------------- #
    @app.errorhandler(Exception)
    def handle_any_exc(exc):  # noqa: ANN001
        if isinstance(exc, HTTPException):
            return exc
        app.logger.exception("Unhandled exception: %s", exc)
        return jsonify({"error": str(exc)}), 500

    @app.errorhandler(ClientDisconnected)
    def handle_disconnect(_: ClientDisconnected):  # noqa: D401
        return jsonify({"error": "Connection closed before upload finished"}), 400

    return app