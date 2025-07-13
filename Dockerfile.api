# ---------- Builder stage ----------
FROM python:3.9-slim@sha256:c2a0feb07dedbf91498883c2f8e1e5201e95c91d413e21c3bea780c8aad8e6a7 AS build

# System libs required only at build time (compile gevent & friends)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps *into the builder image*.
COPY requirements.api.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --no-cache-dir -r requirements.api.txt

# Copy application source
COPY . .

# ---------- Runtime stage ----------
FROM python:3.9-slim@sha256:c2a0feb07dedbf91498883c2f8e1e5201e95c91d413e21c3bea780c8aad8e6a7 AS runtime

WORKDIR /app

# Copy only what we need from builder: site‑packages, entrypoints, and our app
COPY --from=build /usr/local/lib/python3.9/site-packages \
                  /usr/local/lib/python3.9/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY --from=build /app /app

# Expose the application port
EXPOSE 3000

# Default command (can be overridden via docker‑compose)
CMD ["gunicorn", "-k", "gevent", "-w", "4", "-b", "0.0.0.0:3000", "main:create_app()"]