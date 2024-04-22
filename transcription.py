import threading
import time

from openai import OpenAI

from settings import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)


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
            # os.remove(file_path)  # Ensure cleanup of the temp file
            request_queue.put(time.time())  # Signal completion

    # Run transcription in a separate thread
    threading.Thread(target=transcribe).start()
