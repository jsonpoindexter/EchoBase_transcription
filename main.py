import os
import traceback
import mutagen
import werkzeug
import uuid
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from werkzeug.exceptions import ClientDisconnected
from werkzeug.middleware.proxy_fix import ProxyFix

from werkzeug.utils import secure_filename

# ---- Swagger / OpenAPI ----
from flask_swagger_generator.generators import Generator
from flask_swagger_generator.utils import SwaggerVersion
from flask_swagger_generator.utils import SecurityType

# Swagger‑UI (served locally)
from flask_swagger_ui import get_swaggerui_blueprint

from auth import check_api_key
from call_handler.call_handler import start_file_watcher
from config import FLASK_API_KEY, FLASK_BASE_PATH, FLASK_RATE_LIMIT, FLASK_PORT, WHISPER_LANGUAGE, \
    WHISPER_INITIAL_PROMPT, CALL_WATCH_PATH
from celery_worker import transcribe_audio
from sse.sse_server import create_stream_response

# Define the directory name for storing files
dir_name = "temp"
current_directory = os.getcwd()
TEMP_AUDIO_PATH = os.path.join(current_directory, dir_name)
os.makedirs(TEMP_AUDIO_PATH, exist_ok=True)


def create_app():
    app = Flask(__name__)

    # Pick configuration based on FLASK_ENV
    if os.getenv("FLASK_ENV") == "production":
        app.config.from_object("config.ProductionConfig")
    else:
        app.config.from_object("config.DevelopmentConfig")

    # ---------------------------------
    #  Swagger / OpenAPI configuration
    # ---------------------------------
    swagger_destination_path = os.path.join(current_directory, "static", "swagger.yaml")
    os.makedirs(os.path.dirname(swagger_destination_path), exist_ok=True)

    # Create a Swagger 3.0 generator instance
    generator = Generator.of(SwaggerVersion.VERSION_THREE)

    if CALL_WATCH_PATH and (
            not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    ):
        app.logger.info(f"Watching for new audio files in {CALL_WATCH_PATH}")
        start_file_watcher(CALL_WATCH_PATH)

    app.wsgi_app = ProxyFix(app.wsgi_app)
    limiter = Limiter(app, key_func=lambda: request.headers.get('X-API-KEY'))

    def add_base_path(route: str) -> str:
        """
        Prefix every route with the optional FLASK_BASE_PATH.
        If FLASK_BASE_PATH is empty (the common dev case) we leave the
        route untouched so the path in the OpenAPI spec is `/health`
        instead of `//health`.
        """
        return f"/{FLASK_BASE_PATH}{route}" if FLASK_BASE_PATH else route

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Error: {e}")
        app.logger.error(traceback.format_exc())

        # pass through HTTP errors
        if isinstance(e, werkzeug.exceptions.HTTPException):
            return e

        # handle non-HTTP exceptions
        return jsonify({'error': str(e)}), 500

    @app.before_request
    def before_request():
        app.logger.debug(f"Request: {request}")
        app.logger.debug(f"Request headers: {request.headers}")

    @app.errorhandler(ClientDisconnected)
    def handle_disconnect(e):
        app.logger.warning("Client dropped connection during upload")
        return jsonify({"error": "Connection closed before upload finished"}), 400

    @generator.response(status_code=200, schema={'status': 'ok'})
    @app.route(add_base_path('/health'), methods=['GET'])
    @limiter.limit(FLASK_RATE_LIMIT)
    def health_check(e):
        app.logger.error(f"Error: {e}")
        app.logger.error(traceback.format_exc())
        return jsonify({'status': 'ok'}), 200

    @generator.response(status_code=202, schema={'message': 'string', 'taskId': 'string'})
    @generator.request_body({'file': 'binary'})
    @app.route(add_base_path('/transcribe'), methods=['POST'])
    @check_api_key(FLASK_API_KEY)
    @limiter.limit(FLASK_RATE_LIMIT)
    def handle_transcribe_audio():
        print("handle_transcribe_audio")
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']

        # Save the uploaded file to disk
        file_path = os.path.join(TEMP_AUDIO_PATH, secure_filename(file.filename))
        file.save(file_path)

        # Get wav metadata from the file using Mutagen
        if not file_path.lower().endswith(('.wav', '.mp3')):
            return jsonify({'error': 'Unsupported file type'}), 400
        try:
            audio = mutagen.File(file_path)

            if audio is None:
                return jsonify({'error': 'Invalid audio file'}), 400

            app.logger.debug(audio.info)

        except Exception as e:
            app.logger.error(f"Error reading audio file metadata: {e}")
            return jsonify({'error': 'Invalid audio file'}), 400

        # Call the transcribe_audio task asynchronously
        task = transcribe_audio.delay(file.filename, file_path, prompt=WHISPER_INITIAL_PROMPT, language=WHISPER_LANGUAGE)

        # Return a response immediately
        return jsonify({'message': 'Transcription started', "taskId": task.id}), 202

    @app.route('/transcription/events')
    @check_api_key(FLASK_API_KEY)
    def transcription_events():
        client_id = str(uuid.uuid4())
        return create_stream_response(client_id)

    # Generate the swagger.yaml file before attaching UI so /docs routes
    # do not appear in the spec
    generator.generate_swagger(app, destination_path=swagger_destination_path)

    # Serve Swagger‑UI at /docs using the swagger.yaml we just generated
    swaggerui_blueprint = get_swaggerui_blueprint(
        "/docs",                         # Swagger UI endpoint
        "/static/swagger.yaml",          # API spec location
        config={                         # UI config overrides
            "app_name": "EchoBase API Docs",
            "docExpansion": "none",
        },
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix="/docs")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], port=FLASK_PORT)
