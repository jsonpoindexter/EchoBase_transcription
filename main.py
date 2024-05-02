import logging
import os

from flask import Flask, request, jsonify
from flask_limiter import Limiter
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

# Load the Whisper model
model = load_model()


def add_base_path(route):
    return f"/{FLASK_BASE_PATH}{route}"


@app.before_request
def before_request():
    app.logger.debug(f"Request: {request}")


@app.route(add_base_path('/transcribe'), methods=['POST'])
@check_api_key(FLASK_API_KEY)
@limiter.limit(FLASK_RATE_LIMIT)
def handle_transcribe_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    print(f"Received file: {file}")
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    return transcribe_audio(file, model, TEMP_AUDIO_PATH)


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=FLASK_PORT)
