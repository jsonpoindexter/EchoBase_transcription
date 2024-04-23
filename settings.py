import os

from dotenv import load_dotenv


def get_env(key, convert_func):
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Environment variable {key} is not set in .env file")
    try:
        return convert_func(value)
    except ValueError:
        raise ValueError(f"Environment variable {key} could not be converted to the desired type")


load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

AUDIO_STREAM_URL = os.getenv('AUDIO_STREAM_URL')
AUDIO_STREAM_CHUNK_SIZE = get_env('AUDIO_STREAM_CHUNK_SIZE', int)
AUDIO_STREAM_FORMAT = os.getenv('AUDIO_STREAM_FORMAT')
AUDIO_STREAM_BITRATE = get_env('AUDIO_STREAM_BITRATE', int)
AUDIO_STREAM_SAMPLE_RATE = get_env('AUDIO_STREAM_SAMPLE_RATE', int)
AUDIO_STREAM_CHANNELS = get_env('AUDIO_STREAM_CHANNELS', int)

AUDIO_LISTEN_BUFFER_MAX = get_env('AUDIO_LISTEN_BUFFER_MAX', int)

TRANSCRIPTION_MINIMUM_DURATION = get_env('TRANSCRIPTION_MINIMUM_DURATION', int)
TRANSCRIPTION_SILENCE_THRESHOLD = get_env('TRANSCRIPTION_SILENCE_THRESHOLD', int)
TRANSCRIPTION_SILENCE_MINIMUM_DURATION = get_env('TRANSCRIPTION_SILENCE_MINIMUM_DURATION', int)
TRANSCRIPTION_MINIMUM_BYTES = AUDIO_STREAM_BITRATE * TRANSCRIPTION_MINIMUM_DURATION * 128 * AUDIO_STREAM_CHANNELS
