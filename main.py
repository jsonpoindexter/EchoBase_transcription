# main.py
import threading
from queue import Queue

from audio_stream import stream_audio
from settings import AUDIO_URL


def main():
    request_queue = Queue()
    audio_url = AUDIO_URL
    threading.Thread(target=stream_audio, args=(audio_url, request_queue)).start()


if __name__ == '__main__':
    main()
