import os
import traceback
import mutagen
import werkzeug
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

from auth import check_api_key
from config import FLASK_API_KEY, FLASK_BASE_PATH, FLASK_RATE_LIMIT, FLASK_PORT, WHISPER_LANGUAGE, \
    WHISPER_INITIAL_PROMPT
from celery_worker import transcribe_audio

# Define the directory name for storing files
dir_name = "temp"
current_directory = os.getcwd()
TEMP_AUDIO_PATH = os.path.join(current_directory, dir_name)
os.makedirs(TEMP_AUDIO_PATH, exist_ok=True)


def create_app():
    app = Flask(__name__)

    app.wsgi_app = ProxyFix(app.wsgi_app)
    limiter = Limiter(app, key_func=lambda: request.headers.get('X-API-KEY'))

    def add_base_path(route):
        return f"/{FLASK_BASE_PATH}{route}"

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
        transcribe_audio.delay(file.filename, file_path, prompt=WHISPER_INITIAL_PROMPT, language=WHISPER_LANGUAGE)

        # Return a response immediately
        return jsonify({'message': 'Transcription started'}), 202

    return app


# if __name__ != '__main__':
#     print("Starting Flask app != __main__")
#     gunicorn_logger = logging.getLogger('gunicorn.error')
#     app.logger.handlers = gunicorn_logger.handlers
#     app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    app = create_app()
    print("Starting Flask app == __main__")
    app.run(host='0.0.0.0', debug=True, port=FLASK_PORT)
