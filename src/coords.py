"""Parse coordinates from GBIF records and CSV rows."""

from __future__ import annotations

import math


def parse_coordinate(value: object) -> float | None:
    """Return a finite float, or None when the value is missing or unusable.

    Booleans are rejected. True would otherwise pass through float() as 1.0.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, str):
        text = value.strip()
        if text == "" or text.lower() in {"null", "none", "nan", "na"}:
            return None
        try:
            number = float(text)
        except ValueError:
            return None
    else:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
    if not math.isfinite(number):
        return None
    return number
