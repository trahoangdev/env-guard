# Env Guard

FastAPI service to validate environment variables against templates, detect drift, and generate config docs.

## Features
- Validate `.env` against `.env.example` (missing, empty, extra)
- Validate value rules (type, allowed values, regex)
- Generate `docs/config.md` from `.env.example`
- Diff two `.env` files (drift detection)
- Simple API for CI or tooling pipelines

## Quickstart

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir src
```

## Web UI

Open `http://127.0.0.1:8000/` to upload env files, view validation/diff results, and generate docs.
History entries link to detail pages with JSON download.

## API

- `GET /health`
- `GET /api/v1/env/status`
- `POST /api/v1/env/validate` (multipart: `env_file`, optional `example_file`)
- `GET /api/v1/env/report`
- `GET /api/v1/env/history` (query: `limit`)
- `GET /api/v1/env/history/{report_id}`
- `POST /api/v1/env/diff` (multipart: `base_env_file`, `compare_env_file`)
- `GET /api/v1/env/diff/report`
- `GET /api/v1/env/diff/history` (query: `limit`)
- `GET /api/v1/env/diff/history/{report_id}`
- `POST /api/v1/env/docs` (multipart: optional `example_file`)

## Notes
- `.env.example` is the source of truth for required variables.
- If `example_file` is not provided, the service uses the local `.env.example`.
- Do not commit real secrets.
- Reports are persisted locally in `data/env_guard.db`.
- Override DB path via `ENV_GUARD_DB`.

## Validation rules

Rules are defined in comment lines above each variable using `|` separators:

```
# Logging level | allowed=debug,info,warning,error | allowed_ci=true | aliases=warn,err
LOG_LEVEL=info
# Server port | type=int | min=1024 | max=65535
PORT=8000
# Required secret token | pattern=^[A-Za-z0-9_\\-]{12,}$ | min_len=12 | message=Token must be 12+ safe chars
SECRET_TOKEN=
```

Supported constraints:
- `type` (int, float, bool)
- `allowed` with optional `allowed_ci`
- `pattern` (regex)
- `min` / `max` (numeric)
- `min_len` / `max_len` (string length)
- `aliases` (extra enum aliases)
- `message` (custom error message, supports `{code}` and `{value}`)

## CLI

```bash
pip install -e .
envguard validate --example .env.example --env .env
envguard docs --example .env.example --out docs/config.md
envguard diff --base .env --compare .env.staging
```

```bash
python scripts/envguard_cli.py validate --example .env.example --env .env
python scripts/envguard_cli.py docs --example .env.example --out docs/config.md
python scripts/envguard_cli.py diff --base .env --compare .env.staging
```
