# Env Guard

FastAPI service to validate environment variables against templates, detect drift, and generate config docs.

## Features
- Validate `.env` against `.env.example` (missing, empty, extra)
- Generate `docs/config.md` from `.env.example`
- Simple API for CI or tooling pipelines

## Quickstart

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir src
```

## API

- `GET /health`
- `GET /api/v1/env/status`
- `POST /api/v1/env/validate` (multipart: `env_file`, optional `example_file`)
- `GET /api/v1/env/report`
- `POST /api/v1/env/docs` (multipart: optional `example_file`)

## Notes
- `.env.example` is the source of truth for required variables.
- If `example_file` is not provided, the service uses the local `.env.example`.
- Do not commit real secrets.
