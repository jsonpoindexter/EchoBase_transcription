import pyaudio
import webrtcvad
from dotenv import load_dotenv
import os
from openai import OpenAI
import threading
import wave
import tempfile
import time
from queue import Queue, Empty

load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def is_speech(audio_frame, sample_rate, vad):
    """Check if the audio frame contains speech."""
    return vad.is_speech(audio_frame, sample_rate)

def transcribe_audio(file_path, file_name, request_queue):
    """Transcribe the audio using OpenAI's API."""
    while True:
        try:
            try:
                # Check if we can proceed based on the rate limit
                last_request_time = request_queue.get_nowait()
                elapsed_time = time.time() - last_request_time
                if elapsed_time < 20:  # Wait if it's less than 20 seconds since the last request
                    time.sleep(20 - elapsed_time)
            except Empty:
                pass

            with open(file_path, 'rb') as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            print(f"Transcription of {file_name}: {response['data']['text']}")
            request_queue.put(time.time())
            break
        except Exception as e:
            print(f"Failed to transcribe {file_name}: {str(e)}")
            break
        finally:
            os.remove(file_path)  # Ensure temporary files are cleaned up even on failure


def save_and_transcribe(chunk, index, request_queue):
    """Save chunk to a WAV file and start a transcription thread."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav", mode='wb') as f:
        f.write(b'RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00@\x1f\x00\x00@\x1f\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00' + chunk)
        temp_path = f.name
    # Start transcription in a separate thread
    thread = threading.Thread(target=transcribe_audio, args=(temp_path, f"Chunk {index}", request_queue))
    thread.start()

def main():
    vad = webrtcvad.Vad(1)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=160)

    print("Recording...")
    frames = []
    active_speech = False
    request_queue = Queue(maxsize=3)  # Initialize the queue with a size to hold timestamps

    try:
        while True:
            frame = stream.read(160)
            if is_speech(frame, 16000, vad):
                if not active_speech:
                    active_speech = True
                frames.append(frame)
            else:
                if active_speech:
                    # Transition from speech to silence, process current speech chunk
                    speech_chunk = b''.join(frames)
                    save_and_transcribe(speech_chunk, len(frames), request_queue)
                    frames = []
                    active_speech = False
    except KeyboardInterrupt:
        print("Stopped recording.")

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == '__main__':
    main()
