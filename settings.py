import os

from dotenv import load_dotenv

load_dotenv()

AUDIO_URL = os.getenv('AUDIO_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

MINIMUM_DURATION = 0.  # minimum duration for a valid audio segment
SAMPLE_RATE = 16000  # Sample rate to consider for duration calculation
CHUNK_BYTES = 4096  # Number of bytes to read per request.iter_content chunk
# Calculate minimum bytes to fetch based on sample rate and minimum duration
MINIMUM_BYTES = int((SAMPLE_RATE * 2 * MINIMUM_DURATION) / CHUNK_BYTES) * CHUNK_BYTES
