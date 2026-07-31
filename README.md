# Event Embedding Ingest

A Pub/Sub-triggered Google Cloud Function that ingests event messages, generates their vector embeddings via Vertex AI, and stores them in a PostgreSQL/`pgvector` database — for later semantic search/retrieval.

## Requirements

- Python 3.x
- A PostgreSQL database with the `pgvector` extension enabled
- Google Cloud credentials with access to Secret Manager (database credentials are fetched via `get_secret`, not read from plain env vars) and Vertex AI (`langchain-google-vertexai` generates the embeddings)
- Dependencies in `requirements.txt`, notably `functions-framework` (local/dev server for Cloud Functions), `flask-sqlalchemy`, `psycopg2-binary`, `pgvector`, and `langchain-google-vertexai`

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your values
```

### Environment variables

See `.env.example` for the full list. Key ones:

- `ENV` — `dev` or `prod`, selects the config class in `config.py` (default: `dev`)
- `GOOGLE_CLOUD_PROJECT` — GCP project ID
- `CLOUD_VAR` — set automatically in Cloud Run/Cloud Functions; used to detect whether the code is running locally or deployed (affects which DB host secret is used)
- `EMBEDDING_MODEL_NAME` — Vertex AI embedding model used to generate the 768-dim vectors (e.g. `text-embedding-004`)
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

1. Receives a Pub/Sub `CloudEvent` and base64-decodes the message payload into text.
2. Initializes a PostgreSQL connection (`init_db`) using credentials resolved from Secret Manager.
3. Generates a 768-dimension embedding for the message text via `VertexAIEmbeddings` (model set by `EMBEDDING_MODEL_NAME`).
4. Calls `EventController.create_event(...)`, which validates the embedding vector's dimensionality, then inserts a new `EventEmbedding` row (UUID, original message text, embedding vector, timestamp).
5. Logs success/failure; on unhandled exceptions, returns a 500.

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

- No tests.
