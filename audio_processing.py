import os


def process_audio(file, save_directory):
    # Save the FileStorage object to a file in the specified directory
    file_path = os.path.join(save_directory, file.filename)
    file.save(file_path)

    return file_path
