"""Load, filter, and normalize occurrence records."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import pandas as pd

from services.data.gbif import fetch_gbif, include_record
from src.settings import Settings
from src.validate import validate_points


def species_slug(name: str) -> str:
    pieces = []
    current = []
    for character in name:
        if character.isalnum():
            current.append(character)
        elif current:
            pieces.append("".join(current))
            current = []
    if current:
        pieces.append("".join(current))
    return "_".join(pieces)


def _text(value: object) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    text = str(value).strip()
    if text == "" or text.lower() in {"nan", "none", "null"}:
        return None
    return text


def _key(raw: dict, fallback: int) -> int:
    value = raw.get("gbifID", raw.get("gbif_key", raw.get("key")))
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return fallback
    return int(value)


def normalize(raw: dict, fallback_key: int, scientific_name: str) -> dict:
    name = (
        _text(raw.get("species"))
        or _text(raw.get("scientificName"))
        or _text(raw.get("scientific_name"))
        or scientific_name
    )
    return {
        "gbif_key": _key(raw, fallback_key),
        "scientific_name": name,
        "latitude": float(raw["decimalLatitude"]),
        "longitude": float(raw["decimalLongitude"]),
        "event_date": _text(raw.get("eventDate", raw.get("event_date"))),
        "decimalLatitude": float(raw["decimalLatitude"]),
        "decimalLongitude": float(raw["decimalLongitude"]),
    }


def prepare_records(raw_rows: list[dict], scientific_name: str) -> list[dict]:
    """Apply the basis filter, then GBIF coordinate validation, then normalize."""
    candidates = [row for row in raw_rows if include_record(row)]
    valid = validate_points(candidates)
    prepared: list[dict] = []
    seen: set[int] = set()
    for index, raw in enumerate(valid, start=1):
        record = normalize(raw, fallback_key=index, scientific_name=scientific_name)
        if record["gbif_key"] in seen:
            continue
        seen.add(record["gbif_key"])
        prepared.append(record)
    return prepared


def read_fixture_rows(path: Path) -> list[dict]:
    frame = pd.read_csv(path, dtype={"basisOfRecord": "string", "occurrenceStatus": "string"})
    rows = frame.to_dict(orient="records")
    cleaned = []
    for row in rows:
        item = {}
        for key, value in row.items():
            if pd.isna(value):
                item[key] = None
            else:
                item[key] = value
        cleaned.append(item)
    return cleaned


def load_occurrence_rows(settings: Settings, client=None) -> list[dict]:
    if settings.data_mode == "fixture":
        return read_fixture_rows(settings.fixture_dir / "occurrences.csv")
    cache_path = settings.cache_dir / "gbif" / f"{species_slug(settings.scientific_name)}.json"
    if cache_path.exists() and os.environ.get("REFRESH_DATA") != "1":
        return json.loads(cache_path.read_text(encoding="utf-8"))
    raw_rows = fetch_gbif(settings.scientific_name, settings.gbif_limit, client=client)
    slim = [_slim(row) for row in raw_rows]
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(slim), encoding="utf-8")
    return slim


def _slim(raw: dict) -> dict:
    return {
        "gbifID": raw.get("gbifID", raw.get("key")),
        "decimalLatitude": raw.get("decimalLatitude"),
        "decimalLongitude": raw.get("decimalLongitude"),
        "scientificName": raw.get("scientificName"),
        "species": raw.get("species"),
        "eventDate": raw.get("eventDate"),
        "basisOfRecord": raw.get("basisOfRecord"),
        "occurrenceStatus": raw.get("occurrenceStatus"),
    }
