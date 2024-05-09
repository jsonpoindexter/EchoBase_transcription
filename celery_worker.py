import os

from celery import Celery

import time
from config import WHISPER_LANGUAGE
from model import ModelLoader

transcription_worker = Celery("transcriptionTasks", broker="redis://redis:6379", backend="redis://redis:6379")


@transcription_worker.task
def transcribe_audio(
        file_name,
        file_path,
        # prompt,
        # temperature,
        # language=WHISPER_LANGUAGE
):
    print("Transcribing audio file")
    print(f"Transcribing audio file: {file_path}")
    model = ModelLoader.get_model()
    # with open(file_path, 'rb') as file:
    #     print(f"Parameters: {file}")
    try:

        # local_file_path = process_audio(file, temp_audio_path)

        # Read file metadata

        print(f"Metadata:  {os.stat(file_path)}")

        transcribe_args = {
            'audio': file_path,
            # 'prompt': prompt,
            'verbose': True,
        }

        # if language is not None:
        #     transcribe_args['language'] = language
        # else:
        transcribe_args['language'] = WHISPER_LANGUAGE
        #
        # if temperature is not None:
        #     transcribe_args['temperature'] = temperature

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

        result['file_name'] = file_name
        result['duration'] = duration

        return result

    except Exception as e:
        return e
