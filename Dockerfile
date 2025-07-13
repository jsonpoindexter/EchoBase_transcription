FROM python:3.9-slim

# System libs required to build gevent / greenlet C extensions
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libffi-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container to /app
WORKDIR /app

COPY . .

RUN pip3 install --no-cache-dir -r requirements.api.txt

# Make port 3000 available to the world outside this container
EXPOSE 3000

# Run main.py when the container launches
CMD ["python3", "-u",  "main.py"]