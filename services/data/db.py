"""Postgres occurrence table."""

from __future__ import annotations

import time
from pathlib import Path

import psycopg

from src.sql import cell_count_sql

SCHEMA_PATH = Path(__file__).with_name("schema.sql")
INSERT = """
INSERT INTO occurrences (gbif_key, scientific_name, latitude, longitude, event_date)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (gbif_key) DO NOTHING
"""


def connect(database_url: str, retries: int = 30):
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            return psycopg.connect(database_url, connect_timeout=5)
        except psycopg.OperationalError as exc:
            last_error = exc
            if attempt == retries - 1:
                break
            time.sleep(1)
    raise RuntimeError(f"could not connect to Postgres: {last_error}")


def replace_occurrences(database_url: str, records: list[dict]) -> None:
    """Replace the occurrence table with the validated records for this run."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    rows = [
        (
            int(record["gbif_key"]),
            record["scientific_name"],
            float(record["latitude"]),
            float(record["longitude"]),
            record.get("event_date"),
        )
        for record in records
    ]
    with connect(database_url) as conn:
        with conn.cursor() as cursor:
            cursor.execute(schema)
            cursor.execute("TRUNCATE occurrences")
            if rows:
                cursor.executemany(INSERT, rows)
        conn.commit()


def fetch_cell_counts(database_url: str) -> list[dict]:
    with psycopg.connect(database_url, connect_timeout=5) as conn:
        with conn.cursor() as cursor:
            cursor.execute(cell_count_sql())
            fetched = cursor.fetchall()
    return [
        {"lat_cell": int(lat_cell), "lon_cell": int(lon_cell), "n_records": int(n_records)}
        for lat_cell, lon_cell, n_records in fetched
    ]
