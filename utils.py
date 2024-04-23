import tempfile


def save_to_file(file_type, audio_segment):
    """Save AudioSegment to an audio file"""
    # Create a temporary file that persists after closing (delete=False)
    with tempfile.NamedTemporaryFile(suffix=f".{file_type}", delete=False, mode='wb') as temp_file:
        temp_path = temp_file.name  # Store the file path to return later

    # Export the audio segment to the file outside of the with-block to ensure the file is closed
    audio_segment.export(temp_path, format=file_type)

    print(f"Saved audio to {temp_path}")
    return temp_path
