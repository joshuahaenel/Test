"""Local SQLite storage for a user-managed weekly training plan.

No external fitness service integration — the plan is just free text per
weekday, edited directly in the dashboard widget.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "jarvis_training.db"

DAYS_OF_WEEK = [
    "Montag",
    "Dienstag",
    "Mittwoch",
    "Donnerstag",
    "Freitag",
    "Samstag",
    "Sonntag",
]

SCHEMA = """
CREATE TABLE IF NOT EXISTS training_plan (
    day_of_week TEXT PRIMARY KEY,
    description TEXT NOT NULL
);
"""


class InvalidDayError(ValueError):
    pass


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def get_plan(conn: sqlite3.Connection | None = None) -> dict:
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        cursor = conn.execute("SELECT day_of_week, description FROM training_plan")
        stored = {row["day_of_week"]: row["description"] for row in cursor.fetchall()}
        return {day: stored.get(day, "") for day in DAYS_OF_WEEK}
    finally:
        if owns_conn:
            conn.close()


def set_day(day: str, description: str, conn: sqlite3.Connection | None = None) -> dict:
    if day not in DAYS_OF_WEEK:
        raise InvalidDayError(f"Unbekannter Wochentag: {day}")
    owns_conn = conn is None
    conn = conn or get_connection()
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO training_plan (day_of_week, description) VALUES (?, ?)
                ON CONFLICT(day_of_week) DO UPDATE SET description = excluded.description
                """,
                (day, description),
            )
        return {"day": day, "description": description}
    finally:
        if owns_conn:
            conn.close()
