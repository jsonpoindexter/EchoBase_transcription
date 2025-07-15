# EchoBaseTranscription

High‑performance Flask + Celery service that transcribes audio using OpenAI
Whisper (or Faster‑Whisper) and streams the results via SSE.  
The stack is fully containerised and supports **instant hot‑reload for local
development** while producing **tiny, bandwidth‑friendly images for field
deployment**.

---

## Table of Contents
1. [Architecture](#architecture)
2. [Prerequisites](#prerequisites)
3. [Repository Layout](#repository-layout)
4. [Environment Variables](#environment-variables)
5. [Quick Start — Local Dev](#quick-start--local-dev)
6. [Day‑to‑Day Developer Workflow](#day-to-day-developer-workflow)
7. [GPU / CPU Toggle](#gpu--cpu-toggle)
8. [Low‑Bandwidth Deployment Strategy](#low-bandwidth-deployment-strategy)
9. [Production Deployment](#production-deployment)
10. [Updating Dependencies](#updating-dependencies)
11. [Troubleshooting](#troubleshooting)
12. [License](#license)

---

## Architecture

```
+-------------+     SSE       +------------+
|   Flask     | <─────────── |   Browser  |
| (API+UI)  |              +------------+
+-------------+
      │ Celery (Redis broker)
      ▼
+-------------+
|  Worker     |  Whisper / Faster‑Whisper
+-------------+
```

* **Dockermulti‑stage builds** keep the runtime images slim (no compilers).
* Hot reload is handled by **gunicorn--reload** (API) and
  **watchmedo auto‑restart** (Celery worker).
* A **CUDA base stage** lives in `Dockerfile.worker.base`; both dev and prod
  worker images inherit from it.

---

## Prerequisites
| Tool | Dev workstation | Low‑bw deploy box |
|------|-----------------|-------------------|
| Docker ≥ 24 (BuildKit) | ✔ | ✔ |
| Docker Compose v2      | ✔ | ✔ |
| (Optional) NVIDIAdriver+runtime | if GPU transcode | if GPU present |

---

## Repository Layout

| Path | Purpose |
|------|---------|
| `Dockerfile.api` | Multi‑stage build for the Flask / SSE API |
| `Dockerfile.worker.base` | CUDA+python3.12 build stage (`base`, `dev`, `prod`) |
| `Dockerfile.worker` | Final Celery worker image (copies code only) |
| `docker-compose.yml` | Base compose (dev+ prod shared settings) |
| `docker-compose.override.yml` | Dev‑only tweaks (hot reload, dev base) |
| `docker-compose.prod.yml` | Prod‑only tweaks (Gunicorn workers, prod base) |
| `requirements.*.txt` | Python dependency locks |
| `wheelhouse/` | *Optional* pre‑downloaded wheels for offline builds |
| `README.md` | **You are here** |

---

## Environment Variables

Create a file named **`.env`** at repo root:

```dotenv
# Flask
FLASK_API_KEY=changeme
API_PORT=3000
API_ENV=development        # overridden to production in prod compose
FLASK_RATE_LIMIT=300/minute

# Whisper
WHISPER_MODEL_NAME=medium.en
WHISPER_LANGUAGE=en
WHISPER_INITIAL_PROMPT=

# Device selection: auto | cuda | cpu
WHISPER_DEVICE=auto
# float16 for GPU, int8 for CPU, or auto
WHISPER_COMPUTE_TYPE=auto

# Paths
CALL_WATCH_PATH=/host/recordings

# Database
DATABASE_URL=postgresql://user:password@db:5432/echobase
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=echobase
```

> **GPU vs CPU**  
> To choose the execution device for Whisper/Faster‑Whisper, set  
> `WHISPER_DEVICE=cuda` (GPU), `WHISPER_DEVICE=cpu`, or `WHISPER_DEVICE=auto`  
> (default – picks GPU if available).  
> `WHISPER_COMPUTE_TYPE` is usually `float16` for GPUs and `int8` for CPU.

---

## Quick Start — Local Dev

```bash
# 1 — Clone & cd
git clone https://github.com/<you>/EchoBase_transcription.git
cd EchoBase_transcription

# 2 — Build & boot dev stack (hot‑reload)
docker compose up --build -d

# 3 — Run DB migrations once
docker compose run --rm api alembic upgrade head
```

Open <http://localhost:3000/docs> → interactive Swagger‑UI.

Code changes under `./` instantly restart the API & worker.

---

## Day‑to‑Day Developer Workflow

| Task | Command |
|------|---------|
| Build **only** the worker base image (rare) | `docker compose build worker` |
| Run unit tests inside the API container | `docker compose exec api pytest` |
| Lint | `docker compose exec api ruff check .` |
| Apply latest migrations | docker compose run --rm api alembic upgrade head |
| Stop & clean | `docker compose down -v` |

### Building the dev / prod worker base once

```bash
# Dev base (with watchdog)
docker build -f Dockerfile.worker.base --target dev  -t echobase_transcription-worker:dev .

# Prod base (lean runtime)
docker build -f Dockerfile.worker.base --target prod -t echobase_transcription-worker:prod .
```

You rarely need to touch these unless CUDA or system libs change.

---

## GPU / CPU Toggle

Three ways to switch:

| Scenario | How |
|----------|-----|
| **Local dev on GPU machine** | In `.env`: <br>`WHISPER_DEVICE=cuda` <br>`WHISPER_COMPUTE_TYPE=float16` |
| **Local dev on CPU‑only laptop** | `.env`: `WHISPER_DEVICE=cpu` |
| **Compose profile** | `docker compose --profile gpu up` <br>(`worker` service has a `gpu` profile that enables the NVIDIA runtime) |

If `WHISPER_DEVICE=auto` (default) the app tries CUDA and falls back to CPU.

> **Note:** On machines *without* the NVIDIA container runtime the GPU override
> compose file must be omitted, or Docker will raise  
> `could not select device driver "nvidia" with capabilities: [[gpu]]`.

---

## Low‑Bandwidth Deployment Strategy

Developers might have fast internet; deployment site does **not**.
Follow this checklist before heading off‑grid:

1. **Pre‑download base layers & wheels**

   ```bash
   # wheels
   pip download -r requirements.api.txt -d wheelhouse
   tar czf wheelhouse.tgz wheelhouse

   # large Docker layers
   docker save python:3.12-slim \
               echobase_transcription-worker:prod \
               echobase_api:prod \
     | xz -T0 -9 > echobase_images.tar.xz
   ```

2. **Copy artifacts** to USBdrive / NAS.

3. **On‑site: load & push to local registry**

   ```bash
   xz -d < echobase_images.tar.xz | docker load

   # optional local registry cache
   docker run -d --restart=always -p 5000:5000 --name reg registry:2
   docker tag echobase_api:prod localhost:5000/echobase_api:prod
   docker push localhost:5000/echobase_api:prod
   ```

4. **Build with no external traffic**

   ```bash
   # unpack wheelhouse if present
   tar xzf wheelhouse.tgz
   docker compose -f docker-compose.yml -f docker-compose.prod.yml build \
       --no-cache --pull=false
   ```

   *All APT and pip layers hit the BuildKit cache or wheelhouse; network usage ≈0.*

---

## Production Deployment

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

* **API** runs Gunicorn (`4` workers, Gevent).
* **Worker** uses the `:prod` base image, no watchdog, UID drop.

To update:

```bash
git pull
docker compose ... up -d --build   # rebuilt layers stream from local cache
```

---

## Updating Dependencies

1. Change `requirements.*.txt`.
2. On fast link:

   ```bash
   docker compose build --pull api worker
   pip download -r requirements.api.txt -d wheelhouse   # refresh wheelhouse
   ```

3. Re‑export `wheelhouse.tgz` and new image tar to the low‑bw site.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `apt‑get … Could not get lock /var/lib/apt/lists/lock` | Rebuild with fresh cache or run `docker builder prune`. |
| Hot‑reload not triggering | Confirm bind mount `.:/app` and `watchmedo` output in worker logs. |
| Swagger shows only `/docs` route | Ensure spec generation occurs **before** registering Swagger‑UI BP. |

---

## License

[MIT](LICENSE)