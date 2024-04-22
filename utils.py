import tempfile


def save_to_file(file_type, data):
    """Save chunk to an audio file"""
    with tempfile.NamedTemporaryFile(suffix=f".{file_type}", delete=False, mode='wb') as temp_file:
        temp_path = temp_file.name
        temp_file.write(data)
    return temp_path
