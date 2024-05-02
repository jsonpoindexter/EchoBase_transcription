# Project Name

## Description

This project is a Flask application that uses the Whisper ASR (Automatic Speech Recognition) system for transcribing
audio files. The application is dockerized and can be run in both development and production environments.

## Prerequisites

- Python 3.8 or higher
- Docker
- Docker Compose

## Setup

1. Clone the repository:

```
git clone <repository_url>
```

2. Navigate to the project directory:

```
cd <project_directory>
```

3. Install the required Python packages:

```
pip install -r requirements.txt
```

## Configuration

The application uses environment variables for configuration. These variables are loaded from a `.env` file at the root
of the project. Here's an example `.env` file:

```
FLASK_API_KEY=<your_api_key>
FLASK_PORT=3000
FLASK_BASE_PATH=<base_path>
FLASK_RATE_LIMIT=<rate_limit>
WHISPER_MODEL_NAME=medium.en
```

Replace `<your_api_key>`, `<base_path>`, `<rate_limit>`, and `medium.en` with your actual values.

## Running the Application

You can run the application in development or production mode using Docker Compose.

### Setup

First, build the base Docker image. This image contains the Whisper system and its dependencies.

```
docker build -f Dockerfile.base -t whisper-server_base:latest .
```

### Development

To run the application in development mode:

```
docker-compose up dev
```

### Production

To run the application in production mode:

```
docker-compose up prod
```

## API

The application provides a `/{FLASK_BASE_PATH}/transcribe` endpoint for transcribing audio files.

Example request:

```
POST /transcribe
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
