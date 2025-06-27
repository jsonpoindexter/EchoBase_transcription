import os
import traceback

import werkzeug
from flask import Flask, request, jsonify
from flask_limiter import Limiter
from openai import NotGiven
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename

from auth import check_api_key
from config import FLASK_API_KEY, FLASK_BASE_PATH, FLASK_RATE_LIMIT, FLASK_PORT, WHISPER_LANGUAGE
from celery_worker import transcribe_audio

# Define the directory name for storing files
dir_name = "temp"
current_directory = os.getcwd()
TEMP_AUDIO_PATH = os.path.join(current_directory, dir_name)
os.makedirs(TEMP_AUDIO_PATH, exist_ok=True)

PROMPT = """
Phonetic alphabet: Adam Boy Charles David Edward Frank George Henry Ida John King Lincoln Mary Nora Ocean Paul Queen Robert Sam Tom Union Victor William X-ray Young Zebra.
Radio codes: 10-1 poor reception 10-2 good reception 10-4 acknowledge 10-5 relay 10-6 traffic stop 10-7 out of service 10-8 in service 10-9 repeat 10-10 fight in progress
10-12 stand-by 10-13 weather check 10-18 expedite 10-19 return to base 10-20 location 10-21 phone dispatch 10-22 disregard 10-23 on scene 10-24 mission complete.
Nevada agencies & talk-groups: NHP Northern Command West Dispatch NHP Las Vegas Tac Reno Police Dispatch Sparks Police Washoe County Sheriff NDOT Freeway Service Patrol
Storey County Sheriff Nevada Energy Ops.
Typical unit call-signs: Adam units Baker units Charles units David units Frank units George units Henry units Ida units Lincoln units Mary units Nora units Sam units
Union units Victor units William units.
Common phrases: “Dispatch, Adam-21 traffic stop I-80 eastbound mile-marker 45 plate 8-Victor-Boy-Edward-718.” “Central, Charles-12 Code-4.” “Control, Nora-31 10-20 Gate 5.”
Local geography: Reno Sparks Carson City Washoe County Storey County I-80 US-395 Pyramid Highway Virginia Street McCarran Boulevard.
""".strip()


# Initialize the Flask-Limiter extension

def create_app():
    app = Flask(__name__)

    # app.config.from_mapping(
    #     CELERY=dict(
    #         broker_url='redis://redis:6379',
    #         result_backend='redis://redis:6379',
    #         task_ignore_result=True,
    #     ),
    # )
    #
    # celery = Celery(app.name, broker=app.config['CELERY']['broker_url'])
    # celery.conf.update(app.config)

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
        print("Before request")
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

        # Call the transcribe_audio task asynchronously
        transcribe_audio.delay(file.filename, file_path, prompt=PROMPT, language=WHISPER_LANGUAGE)

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
