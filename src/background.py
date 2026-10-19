"""Background points for a presence-background model."""

from __future__ import annotations

import math
import random


def sample_background(
    min_longitude: float,
    min_latitude: float,
    max_longitude: float,
    max_latitude: float,
    n: int,
    seed: int,
) -> list[dict]:
    """Draw n points uniformly inside the bounding box.

    The box is closed. Draws are uniform in degree space, not equal-area.
    The same seed returns the same points. Each record uses GBIF field names.
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    bounds = {
        "min_longitude": min_longitude,
        "min_latitude": min_latitude,
        "max_longitude": max_longitude,
        "max_latitude": max_latitude,
    }
    parsed: dict[str, float] = {}
    for name, value in bounds.items():
        if isinstance(value, bool):
            raise TypeError(f"{name} must be a number")
        try:
            number = float(value)
        except (TypeError, ValueError) as exc:
            raise TypeError(f"{name} must be a number") from exc
        if not math.isfinite(number):
            raise ValueError(f"{name} must be finite")
        parsed[name] = number
    if parsed["min_longitude"] >= parsed["max_longitude"]:
        raise ValueError("longitude bounds must span a positive width")
    if parsed["min_latitude"] >= parsed["max_latitude"]:
        raise ValueError("latitude bounds must span a positive height")
    if n == 0:
        return []
    rng = random.Random(seed)
    points: list[dict] = []
    for _ in range(n):
        longitude = rng.uniform(parsed["min_longitude"], parsed["max_longitude"])
        latitude = rng.uniform(parsed["min_latitude"], parsed["max_latitude"])
        points.append(
            {
                "decimalLongitude": longitude,
                "decimalLatitude": latitude,
            }
        )
    return points
