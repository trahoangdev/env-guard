from __future__ import annotations

import json
import os
import sqlite3
from dataclasses import asdict
from pathlib import Path
from typing import List, Optional

from app.services import env_service

DEFAULT_DB_PATH = Path("data") / "env_guard.db"


def _db_path() -> Path:
    override = os.getenv("ENV_GUARD_DB")
    if override:
        return Path(override)
    return DEFAULT_DB_PATH


def _ensure_db() -> None:
    db_path = _db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS validation_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS diff_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                payload TEXT NOT NULL
            )
            """
        )


def save_validation_report(report: env_service.ValidationReport) -> int:
    _ensure_db()
    payload = json.dumps(asdict(report))
    with sqlite3.connect(_db_path()) as conn:
        cursor = conn.execute(
            "INSERT INTO validation_reports (created_at, payload) VALUES (datetime('now'), ?)",
            (payload,),
        )
        return int(cursor.lastrowid)


def save_diff_report(report: env_service.DiffReport) -> int:
    _ensure_db()
    payload = json.dumps(asdict(report))
    with sqlite3.connect(_db_path()) as conn:
        cursor = conn.execute(
            "INSERT INTO diff_reports (created_at, payload) VALUES (datetime('now'), ?)",
            (payload,),
        )
        return int(cursor.lastrowid)


def list_validation_reports(limit: int = 20) -> List[dict]:
    _ensure_db()
    with sqlite3.connect(_db_path()) as conn:
        rows = conn.execute(
            "SELECT id, created_at, payload FROM validation_reports ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {"id": row[0], "created_at": row[1], "payload": json.loads(row[2])}
        for row in rows
    ]


def list_diff_reports(limit: int = 20) -> List[dict]:
    _ensure_db()
    with sqlite3.connect(_db_path()) as conn:
        rows = conn.execute(
            "SELECT id, created_at, payload FROM diff_reports ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {"id": row[0], "created_at": row[1], "payload": json.loads(row[2])}
        for row in rows
    ]


def get_validation_report(report_id: int) -> Optional[dict]:
    _ensure_db()
    with sqlite3.connect(_db_path()) as conn:
        row = conn.execute(
            "SELECT id, created_at, payload FROM validation_reports WHERE id = ?",
            (report_id,),
        ).fetchone()
    if row is None:
        return None
    return {"id": row[0], "created_at": row[1], "payload": json.loads(row[2])}


def get_diff_report(report_id: int) -> Optional[dict]:
    _ensure_db()
    with sqlite3.connect(_db_path()) as conn:
        row = conn.execute(
            "SELECT id, created_at, payload FROM diff_reports WHERE id = ?",
            (report_id,),
        ).fetchone()
    if row is None:
        return None
    return {"id": row[0], "created_at": row[1], "payload": json.loads(row[2])}
