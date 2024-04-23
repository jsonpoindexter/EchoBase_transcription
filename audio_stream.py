import io
import threading

import requests
from pydub import AudioSegment, silence, playback

from settings import TRANSCRIPTION_MINIMUM_DURATION, TRANSCRIPTION_MINIMUM_BYTES, AUDIO_LISTEN_BUFFER_MAX, \
    AUDIO_STREAM_CHUNK_SIZE, AUDIO_STREAM_SAMPLE_RATE, AUDIO_STREAM_FORMAT, TRANSCRIPTION_SILENCE_MINIMUM_DURATION, \
    TRANSCRIPTION_SILENCE_THRESHOLD
from transcription import send_for_transcription
from utils import save_to_file

print(f"Bytes needed: {TRANSCRIPTION_MINIMUM_BYTES} for {TRANSCRIPTION_MINIMUM_DURATION} seconds")


class BufferHandler:
    def __init__(self, format, sample_rate, buffer_max):
        self.format = format
        self.sample_rate = sample_rate
        self.buffer_max = buffer_max
        self.buffer = io.BytesIO()

    def write_to_buffer(self, chunk):
        self.buffer.write(chunk)
        if self.is_buffer_full():
            self.play_audio_from_buffer()

    def is_buffer_full(self):
        return self.buffer.tell() >= self.buffer_max

    def play_audio_from_buffer(self):
        # print(f"Playing AUDIO buffer")
        self.buffer.seek(0)
        # print("DONE self.buffer.seek(0)")
        audio = AudioSegment.from_file(self.buffer, format=self.format, frame_rate=self.sample_rate)
        # print("DONE AudioSegment.from_file(self.buffer, format='mp3', frame_rate=22050)")
        threading.Thread(target=playback.play, args=(audio,)).start()
        # print(f"DONE playback.play(audio)")
        self.reset_buffer()
        # print(f"DONE self.reset_buffer()")

    def reset_buffer(self):
        self.buffer = io.BytesIO()


def stream_audio(url, request_queue):
    print("Connecting to audio stream...")
    transcription_buffer = AudioSegment.empty()
    buffer_handler = BufferHandler(AUDIO_STREAM_FORMAT, AUDIO_STREAM_SAMPLE_RATE, AUDIO_LISTEN_BUFFER_MAX)
    with requests.get(url, stream=True) as r:
        if r.status_code == 200:
            for chunk in r.iter_content(chunk_size=AUDIO_STREAM_CHUNK_SIZE):
                if chunk:
                    buffer_handler.write_to_buffer(chunk)
                    audio_chunk = AudioSegment.from_file(io.BytesIO(chunk), format=AUDIO_STREAM_FORMAT,
                                                         frame_rate=AUDIO_STREAM_SAMPLE_RATE)
                    transcription_buffer += audio_chunk

                    if len(transcription_buffer) >= TRANSCRIPTION_MINIMUM_BYTES:
                        silence_ranges = silence.detect_silence(transcription_buffer,
                                                                min_silence_len=TRANSCRIPTION_SILENCE_MINIMUM_DURATION,
                                                                silence_thresh=TRANSCRIPTION_SILENCE_THRESHOLD)
                        if silence_ranges:
                            silence_start = silence_ranges[0][0]
                            sentence_audio = transcription_buffer[:silence_start]
                            file_path = save_to_file(AUDIO_STREAM_FORMAT, transcription_buffer)
                            send_for_transcription(file_path, request_queue)
                            transcription_buffer = AudioSegment.empty()
                        else:
                            print("No sufficient silence detected; continuing to accumulate audio.")
                    else:
                        print(
                            f"Transcription buffer size: {len(transcription_buffer)} out of {TRANSCRIPTION_MINIMUM_BYTES} bytes.")
                else:
                    print("Failed to receive chunk")
        else:
            print(f"Failed to connect to stream: {r.status_code}")
