"""Local SQLite storage for Apple Health data delivered by Health Auto Export.

The exact JSON shape sent by Health Auto Export should be confirmed against a
real export before relying on `_extract_samples` in production — the full raw
payload is always stored too, so nothing is lost if the parsing needs
adjusting later.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "jarvis_health.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS health_raw_payloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    received_at TEXT NOT NULL,
    raw_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS health_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    recorded_at TEXT NOT NULL,
    received_at TEXT NOT NULL
);
"""


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def _extract_samples(payload: dict) -> list[dict]:
    samples = []
    metrics = (payload.get("data") or {}).get("metrics") or []
    for metric in metrics:
        name = metric.get("name")
        unit = metric.get("units")
        for entry in metric.get("data", []):
            qty = entry.get("qty")
            date = entry.get("date")
            if name is None or qty is None or date is None:
                continue
            samples.append({"metric": name, "value": qty, "unit": unit, "recorded_at": date})
    return samples


def store_payload(
    payload: dict,
    conn: sqlite3.Connection | None = None,
    now: datetime | None = None,
) -> int:
    """Persists the raw payload and any samples extracted from it. Returns
    the number of samples successfully extracted."""
    owns_conn = conn is None
    conn = conn or get_connection()
    now = now or datetime.now(timezone.utc)
    received_at = now.isoformat()
    try:
        with conn:
            conn.execute(
                "INSERT INTO health_raw_payloads (received_at, raw_json) VALUES (?, ?)",
                (received_at, json.dumps(payload)),
            )
            samples = _extract_samples(payload)
            for sample in samples:
                conn.execute(
                    "INSERT INTO health_samples (metric, value, unit, recorded_at, received_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        sample["metric"],
                        sample["value"],
                        sample["unit"],
                        sample["recorded_at"],
                        received_at,
                    ),
                )
        return len(samples)
    finally:
        if owns_conn:
            conn.close()


def latest_summary(conn: sqlite3.Connection | None = None) -> dict:
    """Returns the most recent sample per metric."""
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        cursor = conn.execute(
            """
            SELECT metric, value, unit, recorded_at, received_at
            FROM health_samples
            WHERE id IN (SELECT MAX(id) FROM health_samples GROUP BY metric)
            ORDER BY metric
            """
        )
        return {"metrics": [dict(row) for row in cursor.fetchall()]}
    finally:
        if owns_conn:
            conn.close()


def recent_samples(
    metric: str | None = None, days: int = 7, conn: sqlite3.Connection | None = None
) -> list[dict]:
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        query = "SELECT metric, value, unit, recorded_at, received_at FROM health_samples"
        params: list = []
        if metric:
            query += " WHERE metric = ?"
            params.append(metric)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(days * 24)
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if owns_conn:
            conn.close()
