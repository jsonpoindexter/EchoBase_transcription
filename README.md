# Audio Transcription Project

This project is designed to transcribe audio from a given URL. It is built with Python and uses the OpenAI API for
transcription.

## Project Structure

The project is organized into several Python files, each with a specific responsibility:

- `settings.py`: Contains all the settings related to the project, such as constants and environment variables.
- `transcription.py`: Contains the logic related to transcribing audio.
- `audio_stream.py`: Contains the logic related to streaming audio.
- `utils.py`: Contains utility functions that can be used across the project.
- `main.py`: Contains the main execution logic of the project.

## Installation

This project requires Python 3.6 or higher.

To install the necessary dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Usage

To run the project, execute the `main.py` file:

```bash
python main.py
```

## Dependencies

This project uses the following Python packages:

- `python-dotenv==1.0.1`
- `requests==2.31.0`
- `openai==1.23.2`

These can be installed using the `requirements.txt` file.

## License

This project is licensed under the terms of the MIT license.
