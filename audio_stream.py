import requests

from settings import CHUNK_BYTES
from transcription import send_for_transcription
from utils import save_to_file


def stream_audio(url, request_queue):
    print("Connecting to audio stream...")
    with requests.get(url, stream=True) as r:
        if r.status_code == 200:
            print("Connected to stream.")
            buffer = bytes()
            for chunk in r.iter_content(chunk_size=CHUNK_BYTES):  # Consider adjusting chunk size as needed
                if chunk:
                    buffer += chunk
                    if len(buffer) >= 32768:  # 32KB before processing
                        file_path = save_to_file("mp3", buffer)
                        send_for_transcription(file_path, request_queue)
                        buffer = bytes()  # Reset the buffer after sending
                else:
                    print("Failed to receive chunk")
        else:
            print(f"Failed to connect to stream: {r.status_code}")
