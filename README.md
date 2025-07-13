# EchoBaseTranscription

High‑performance Flask + Celery service that transcribes audio using OpenAI
Whisper (or Faster‑Whisper) and streams the results via SSE.  
The stack is fully containerised and supports **instant hot‑reload for local
development** while producing **tiny, bandwidth‑friendly images for field
deployment**.

---

## TableofContents
1. [Architecture](#architecture)
2. [Prerequisites](#prerequisites)
3. [Repository Layout](#repository-layout)
4. [EnvironmentVariables](#environment-variables)
5. [QuickStart—LocalDev](#quick-start--local-dev)
6. [Day‑to‑DayDeveloperWorkflow](#day-to-day-developer-workflow)
7. [Low‑BandwidthDeploymentStrategy](#low-bandwidth-deployment-strategy)
8. [ProductionDeployment](#production-deployment)
9. [UpdatingDependencies](#updating-dependencies)
10. [Troubleshooting](#troubleshooting)
11. [License](#license)

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
| Docker≥24(BuildKit) | ✔ | ✔ |
| DockerComposev2      | ✔ | ✔ |
| (Optional) NVIDIAdriver+runtime | if GPU transcode | if GPU present |

---

## RepositoryLayout

| Path | Purpose |
|------|---------|
| `Dockerfile.api` | Multi‑stage build for the Flask / SSE API |
| `Dockerfile.worker.base` | CUDA+Python3.9 build stage (`base`, `dev`, `prod`) |
| `Dockerfile.worker` | Final Celery worker image (copies code only) |
| `docker-compose.yml` | Base compose (dev+ prod shared settings) |
| `docker-compose.override.yml` | Dev‑only tweaks (hot reload, dev base) |
| `docker-compose.prod.yml` | Prod‑only tweaks (Gunicorn workers, prod base) |
| `requirements.*.txt` | Python dependency locks |
| `wheelhouse/` | *Optional* pre‑downloaded wheels for offline builds |
| `README.md` | **You are here** |

---

## EnvironmentVariables

Create a file named **`.env`** at repo root:

```dotenv
# Flask
FLASK_API_KEY=changeme
FLASK_PORT=3000
FLASK_ENV=development        # overridden to production in prod compose
FLASK_RATE_LIMIT=300/minute

# Whisper
WHISPER_MODEL_NAME=medium.en
WHISPER_LANGUAGE=en
WHISPER_INITIAL_PROMPT=

# Paths
CALL_WATCH_PATH=/host/recordings
```

Compose automatically loads this file.

---

## QuickStart—LocalDev

```bash
# 1–clone & cd
git clone https://github.com/<you>/EchoBase_transcription.git
cd EchoBase_transcription

# 2–bring up dev stack (hot‑reload)
docker compose up --build
```

Open <http://localhost:3000/docs> → interactive Swagger‑UI.

Code changes under `./` instantly restart the API & worker.

---

## Day‑to‑DayDeveloperWorkflow

| Task | Command |
|------|---------|
| Build **only** the worker base image (rare) | `docker compose build worker` |
| Run unit tests inside the API container | `docker compose exec api pytest` |
| Lint | `docker compose exec api ruff check .` |
| Recreate DB | `docker compose exec db psql …` |
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

## Low‑BandwidthDeploymentStrategy

Developers might have fast internet; deployment site does **not**.
Follow this checklist before heading off‑grid:

1. **Pre‑download base layers & wheels**

   ```bash
   # wheels
   pip download -r requirements.api.txt -d wheelhouse
   tar czf wheelhouse.tgz wheelhouse

   # large Docker layers
   docker save python:3.9-slim \
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

## ProductionDeployment

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

## UpdatingDependencies

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