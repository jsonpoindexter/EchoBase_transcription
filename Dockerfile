# ---------- Builder stage ----------
FROM python:3.9-slim@sha256:c2a0feb07dedbf91498883c2f8e1e5201e95c91d413e21c3bea780c8aad8e6a7 AS build

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