import time

from flask import jsonify

from audio_processing import process_audio


def transcribe_audio(file, model, temp_audio_path):
    try:
        print(f"File name: {file.filename}")
        print(f"File content type: {file.content_type}")
        print(f"File size: {file.headers.get('Content-Length')}")
        print(f"File MIME type: {file.mimetype}")

        local_file_path = process_audio(file, temp_audio_path)

        # Benchmark the model
        start_time = time.time()
        result = model.transcribe(local_file_path)
        end_time = time.time()
        print(f"Transcription time: {end_time - start_time} seconds")

        print(f"Result: {result}")
        transcription = result['text']
        print(f"Transcription: {transcription}")

        return jsonify({'transcription': transcription})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
