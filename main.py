import logging
import os
import traceback

import werkzeug
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from openai import NotGiven
from werkzeug.middleware.proxy_fix import ProxyFix

from auth import check_api_key
from config import FLASK_API_KEY, FLASK_BASE_PATH, FLASK_RATE_LIMIT, FLASK_PORT
from model import load_model
from transcription import transcribe_audio

# Define the directory name for storing files
dir_name = "temp"
current_directory = os.getcwd()
TEMP_AUDIO_PATH = os.path.join(current_directory, dir_name)
os.makedirs(TEMP_AUDIO_PATH, exist_ok=True)

# Initialize the Flask-Limiter extension
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
limiter = Limiter(app, key_func=lambda: request.headers.get('X-API-KEY'))

# Load the Whisper modelF
model = load_model()


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
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    # model = request.form.get('model', WHISPER_MODEL_NAME) # TODO: support changing models
    language = request.form.get('language', None)
    prompt = request.form.get('prompt', NotGiven)
    temperature = request.form.get('temperature', None)

    # Then pass the parameters to the transcribe_audio function
    return transcribe_audio(
        file=file,
        model=model,
        temp_audio_path=TEMP_AUDIO_PATH,
        prompt=prompt,
        temperature=temperature,
        language=language
    )


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=FLASK_PORT)
