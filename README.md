# Event Embedding Ingest

A Pub/Sub-triggered Google Cloud Function that ingests event messages and stores them, along with their vector embeddings, in a PostgreSQL/`pgvector` database — for later semantic search/retrieval.

> **Status:** early-stage prototype. `main.py` currently calls `EventController.create_event` with placeholder test data (`"Mensaje de prueba"` and a fixed `[0.5] * 768` vector) instead of generating a real embedding from the incoming Pub/Sub message.

## Requirements

- Python 3.x
- A PostgreSQL database with the `pgvector` extension enabled
- Google Cloud credentials with access to Secret Manager (database credentials are fetched via `get_secret`, not read from plain env vars) and Vertex AI (`google-cloud-aiplatform` is a dependency, for embedding generation)
- Dependencies in `requirements.txt`, notably `functions-framework` (local/dev server for Cloud Functions), `flask-sqlalchemy`, `psycopg2-binary`, and `pgvector`

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with the required variables (see [Environment variables](#environment-variables) below).

### Environment variables

- `ENV` — `dev` or `prod`, selects the config class in `config.py` (default: `dev`)
- `GOOGLE_CLOUD_PROJECT` — GCP project ID
- `CLOUD_VAR` — set automatically in Cloud Run/Cloud Functions; used to detect whether the code is running locally or deployed (affects which DB host secret is used)
- Database credentials are **not** read directly from env vars — `config.py` holds the *names* of the Secret Manager secrets (`POSTGRE_USR_RAG_REPO_DEV`, `POSTGRE_PASS_RAG_REPO_DEV`, etc.), which are resolved at runtime via `get_secret()`. Ensure those secrets exist in Secret Manager for your project.

## Running locally

Local execution is handled by [`functions-framework`](https://github.com/GoogleCloudPlatform/functions-framework-python) (listed in `requirements.txt`), which spins up a dev server and dispatches CloudEvents to the `main` function in `main.py`.

```bash
functions-framework --target=main --signature-type=cloudevent --debug
```

- `--target=main` — the function to invoke (`main` in `main.py`)
- `--signature-type=cloudevent` — required, since this function is triggered by a Pub/Sub `CloudEvent`, not a plain HTTP request
- `--debug` — enables live reloading on code changes
- By default the server listens on `http://0.0.0.0:8080`; override with `--port` if needed

To simulate a Pub/Sub trigger locally, send a CloudEvent-formatted request with a base64-encoded `message.data` payload (see the [functions-framework CloudEvent docs](https://github.com/GoogleCloudPlatform/functions-framework-python#run-your-function-on-a-local-development-server) for the exact request shape).

## What it does

1. Receives a Pub/Sub `CloudEvent` and base64-decodes the message payload.
2. Initializes a PostgreSQL connection (`init_db`) using credentials resolved from Secret Manager.
3. Calls `EventController.create_event(...)`, which validates that the embedding vector has exactly 768 dimensions, then inserts a new `EventEmbedding` row (UUID, original message text, embedding vector, timestamp).
4. Logs success/failure; on unhandled exceptions, returns a 500.

## Project structure

```
main.py                          # Cloud Function entrypoint (functions_framework.cloud_event)
__init__.py                      # DB engine/session setup (init_db, get_db_session)
config.py                        # Environment-based config (dev/prod), Secret Manager secret names
controller/
  event_controller.py            # create_event: validates + persists an event embedding
models/
  event_embedding.py             # SQLAlchemy model for the event_embeddings table (pgvector column)
utils/
  utils.py                       # Secret Manager helper (get_secret)
```

## Known gaps

- No real embedding generation yet — the message payload is decoded but not passed through an embedding model; `main.py` sends hardcoded test data instead.
- No tests.
