# AGENTS.md

## Project Overview
- Name: Project 02
- Root: C:\CODE PROJECT 3\CODEX\PROJECT 02
- Stack: Python + FastAPI
- Status: initialized

## Goals
- Build a FastAPI API service with a clear, extensible architecture.
- Standardize development, testing, and release workflows.

## Scope
- Application/Module: REST API + (optional) background jobs
- Language/Framework: Python 3.11+ / FastAPI / Pydantic v2

## General Conventions
- Documentation language: English (technical terms may remain as-is).
- Naming: `kebab-case` for folders, `snake_case` for files, `PascalCase` for classes, `camelCase` for variables/functions.
- Do not commit build artifacts, logs, or secrets (API keys, secrets).
- Each PR/commit should be small and focused on a single goal.

## Directory Structure (recommended)
- `src/`
  - `app/`
    - `main.py` (FastAPI app, router include)
    - `api/` (routers)
      - `v1/` (versioned routes)
    - `schemas/` (Pydantic models)
    - `models/` (ORM models)
    - `services/` (business logic)
    - `core/` (config, settings, security, logging)
    - `db/` (session, migrations)
    - `deps/` (FastAPI dependencies)
    - `tasks/` (background jobs)
  - `tests/`
  - `docs/`
  - `scripts/`
  - `assets/`

## Configuration
- Use `.env` for local settings; commit `.env.example` only.
- Centralize config in `src/app/core/config.py` using `pydantic-settings`.
- Prefer explicit defaults; document every env var in `docs/config.md`.

## API Design
- Version APIs under `/api/v1`.
- Prefer JSON:API-like consistency (resource naming, pagination, errors).
- Use `APIRouter` with tags and response models for all routes.
- Return structured errors with `detail`, `code`, and `meta` fields.

## Logging
- Configure structured logging (JSON or key/value).
- Log request/response metadata at INFO; errors at ERROR with stack traces.
- Avoid logging PII/secrets.

## Database
- Preferred: PostgreSQL with SQLAlchemy + Alembic.
- Use `async` engine/session if async routes are used.
- Keep database access in `services/` or `db/` helpers.
- Migration scripts go in `src/app/db/migrations`.

## Background Jobs
- Lightweight tasks: FastAPI `BackgroundTasks`.
- Heavier workloads: use a queue (e.g., Redis + RQ/Celery) if needed.

## Development Workflow
1) Create a branch from `main` using `feature/<name>` or `fix/<name>`.
2) Create a virtual environment: `python -m venv .venv` and activate it.
3) Install dependencies with `pip` or `poetry` (if chosen).
4) Write code with tests (when possible).
5) Run lint/tests before opening a PR.
6) Write a clear description: goal, key changes, how to test.

## Coding Style
- Prefer clarity over micro-optimizations.
- Limit side effects; separate pure logic and I/O.
- Add short comments for complex logic.
- Avoid duplicate code unless abstraction would reduce clarity.

## Tooling (suggested)
- Lint/format: `ruff` + `black`
- Type check: `mypy` (optional)
- Test: `pytest`, `pytest-asyncio`, `httpx`
- Migration: `alembic` (if using a DB)

## Testing
- Prefer unit tests for core logic.
- For APIs, add integration tests with `httpx`/`TestClient`.
- Every bug fix should include a reproducing test.

## Documentation
- All new APIs/features must be documented in `docs/`.
- When adding config/environment variables, update `docs/config.md`.
- Maintain `docs/api.md` for endpoint overview and examples.

## Security
- Never hard-code secrets.
- Use `.env` and `.env.example` (do not commit real secrets).
- Validate input and handle errors properly.
- Rate-limit sensitive endpoints when exposed publicly.

## Deployment
- Containerize with Docker.
- Use `uvicorn` or `gunicorn` with `uvicorn.workers.UvicornWorker`.
- Health checks: `/health` (liveness) and `/ready` (readiness).

## Commit Rules
- Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.

## Notes
- Update TBD items after defining the database and API scope.
