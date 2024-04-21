import io
import tempfile

import requests
import os
from openai import OpenAI
import time
from queue import Queue
import threading

# Load environment variables and initialize OpenAI client
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Constants for the audio processing
MINIMUM_DURATION = 0.  # minimum duration for a valid audio segment
SAMPLE_RATE = 16000  # Sample rate to consider for duration calculation
CHUNK_BYTES = 4096  # Number of bytes to read per request.iter_content chunk
# Calculate minimum bytes to fetch based on sample rate and minimum duration
MINIMUM_BYTES = int((SAMPLE_RATE * 2 * MINIMUM_DURATION) / CHUNK_BYTES) * CHUNK_BYTES

def send_for_transcription(file_path, request_queue):
    def transcribe():
        try:
            print("Transcribing audio of ", file_path, "...")
            with open(file_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            transcription_text = response.text
            print(f"Transcription: {transcription_text}")
        except Exception as e:
            print(f"Failed to transcribe audio: {str(e)}")
        finally:
            os.remove(file_path)  # Ensure cleanup of the temp file
            request_queue.put(time.time())  # Signal completion

    # Run transcription in a separate thread
    threading.Thread(target=transcribe).start()

def stream_audio(url, request_queue):
    print("Connecting to audio stream...")
    with requests.get(url, stream=True) as r:
        if r.status_code == 200:
            print("Connected to stream.")
            buffer = bytes()
            for chunk in r.iter_content(chunk_size=4096):  # Consider adjusting chunk size as needed
                if chunk:
                    # print("Received chunk of size: ", len(chunk))
                    buffer += chunk
                    if len(buffer) >= 32768:  # 32KB before processing
                        file_path = save_to_file("mp3", buffer)
                        send_for_transcription(file_path, request_queue)
                        buffer = bytes()  # Reset the buffer after sending
                    # else:
                        # print("Buffer length: ", len(buffer), " out of 32768")
                else:
                    print("Failed to receive chunk")
        else:
            print(f"Failed to connect to stream: {r.status_code}")

def save_to_file(file_type, data):
    """Save chunk to an audio file"""
    with tempfile.NamedTemporaryFile(suffix=f".{file_type}", delete=False, mode='wb') as temp_file:
        temp_path = temp_file.name
        temp_file.write(data)
    return temp_path

def main():
    request_queue = Queue()  # Initialize the queue with a size to hold timestamps
    audio_url = "https://broadcastify.cdnstream1.com/7364"
    threading.Thread(target=stream_audio, args=(audio_url, request_queue)).start()

if __name__ == '__main__':
    main()
