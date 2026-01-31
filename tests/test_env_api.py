import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app.main import app

client = TestClient(app)


def test_validate_env() -> None:
    example_content = "# Port | type=int\nPORT=8000\nFOO=\nBAR=1\n"
    env_content = "PORT=abc\nBAR=1\nBAZ=2\n"
    files = {
        "example_file": (".env.example", example_content, "text/plain"),
        "env_file": (".env", env_content, "text/plain"),
    }
    response = client.post("/api/v1/env/validate", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["required_missing"][0]["key"] == "FOO"
    assert payload["extra_keys"][0]["key"] == "BAZ"
    assert payload["invalid_values"][0]["key"] == "PORT"


def test_validate_min_max() -> None:
    example_content = "# Port | type=int | min=1024 | max=65535\nPORT=8000\n"
    env_content = "PORT=80\n"
    files = {
        "example_file": (".env.example", example_content, "text/plain"),
        "env_file": (".env", env_content, "text/plain"),
    }
    response = client.post("/api/v1/env/validate", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["invalid_values"][0]["reason"] == "min_value"


def test_validate_allowed_ci() -> None:
    example_content = "# Level | allowed=debug,info,warning | allowed_ci=true\nLOG_LEVEL=info\n"
    env_content = "LOG_LEVEL=WARNING\n"
    files = {
        "example_file": (".env.example", example_content, "text/plain"),
        "env_file": (".env", env_content, "text/plain"),
    }
    response = client.post("/api/v1/env/validate", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True


def test_diff_env() -> None:
    base_content = "A=1\nB=2\n"
    compare_content = "A=1\nB=3\nC=4\n"
    files = {
        "base_env_file": (".env", base_content, "text/plain"),
        "compare_env_file": (".env.compare", compare_content, "text/plain"),
    }
    response = client.post("/api/v1/env/diff", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is False
    assert payload["extra_in_compare"][0]["key"] == "C"
    assert payload["different_values"][0]["key"] == "B"


def test_docs() -> None:
    example_content = "# App name\nAPP_NAME=EnvGuard\n"
    files = {"example_file": (".env.example", example_content, "text/plain")}
    response = client.post("/api/v1/env/docs", files=files)
    assert response.status_code == 200
    payload = response.json()
    assert "APP_NAME" in payload["markdown"]
