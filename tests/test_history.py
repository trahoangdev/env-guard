from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

import sys

sys.path.insert(0, str(SRC))

from app.main import app

client = TestClient(app)


def test_history_persists_reports(tmp_path: Path, monkeypatch) -> None:
    db_path = tmp_path / "env_guard.db"
    monkeypatch.setenv("ENV_GUARD_DB", str(db_path))

    example_content = "FOO=\n"
    env_content = ""
    files = {
        "example_file": (".env.example", example_content, "text/plain"),
        "env_file": (".env", env_content, "text/plain"),
    }

    response = client.post("/api/v1/env/validate", files=files)
    assert response.status_code == 200

    history = client.get("/api/v1/env/history")
    assert history.status_code == 200
    payload = history.json()
    assert len(payload) >= 1
