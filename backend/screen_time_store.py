"""Local SQLite storage for manually-entered screen time.

Apple provides no export API or Shortcuts action for Screen Time data, so
entries are logged by hand (via the dashboard widget or by telling Jarvis in
chat) rather than synced automatically like Health data.
"""

from __future__ import annotations

import sqlite3
from datetime import date as date_cls
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "jarvis_screen_time.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS screen_time_entries (
    date TEXT PRIMARY KEY,
    minutes INTEGER NOT NULL,
    recorded_at TEXT NOT NULL
);
"""


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def log_entry(
    minutes: int,
    entry_date: str | None = None,
    conn: sqlite3.Connection | None = None,
    now: datetime | None = None,
) -> dict:
    owns_conn = conn is None
    conn = conn or get_connection()
    entry_date = entry_date or date_cls.today().isoformat()
    now = now or datetime.now(timezone.utc)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO screen_time_entries (date, minutes, recorded_at)
                VALUES (?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET minutes = excluded.minutes,
                                                 recorded_at = excluded.recorded_at
                """,
                (entry_date, minutes, now.isoformat()),
            )
        return {"date": entry_date, "minutes": minutes}
    finally:
        if owns_conn:
            conn.close()


def get_history(days: int = 7, conn: sqlite3.Connection | None = None) -> list[dict]:
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        cursor = conn.execute(
            "SELECT date, minutes FROM screen_time_entries ORDER BY date DESC LIMIT ?",
            (days,),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        if owns_conn:
            conn.close()
