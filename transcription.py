import time

from flask import jsonify

from audio_processing import process_audio
from config import WHISPER_LANGUAGE


def transcribe_audio(file, model, temp_audio_path, prompt, temperature, language=WHISPER_LANGUAGE):
    print(f"Parameters: {file}, {model}, {temp_audio_path}, {language}, {prompt}, {temperature}")
    try:
        print(f"File name: {file.filename}")
        print(f"File content type: {file.content_type}")
        print(f"File size: {file.headers.get('Content-Length')}")
        print(f"File MIME type: {file.mimetype}")

        local_file_path = process_audio(file, temp_audio_path)

        transcribe_args = {
            'audio': local_file_path,
            'prompt': prompt,
            'verbose': True,
        }

        if language is not None:
            transcribe_args['language'] = language
        else:
            transcribe_args['language'] = WHISPER_LANGUAGE

        if temperature is not None:
            transcribe_args['temperature'] = temperature

        # Benchmark the model
        start_time = time.time()
        # Only use temperature if it is not None
        result = model.transcribe(**transcribe_args)

        end_time = time.time()
        duration = end_time - start_time
        print(f"Transcription time: {duration} seconds")

        print(f"Result: {result}")
        transcription = result['text']
        print(f"Transcription: {transcription}")

        result['file_name'] = file.filename
        result['duration'] = duration

        return jsonify(result)

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
