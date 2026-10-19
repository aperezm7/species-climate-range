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
    parsed = {}
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
    points = []
    for _ in range(n):
        points.append(
            {
                "decimalLongitude": rng.uniform(parsed["min_longitude"], parsed["max_longitude"]),
                "decimalLatitude": rng.uniform(parsed["min_latitude"], parsed["max_latitude"]),
            }
        )
    return points


EXPLANATION = """
Presence-only data has no absences. Background points are the contrast class: places in the domain where the species was not recorded in this table. Drawing them uniformly inside the presence bounding box is the smallest domain sample. It is not a target-group background, and it is uniform in degrees rather than in area, so cells toward the poles are slightly over-weighted.

The seed is part of the result. A review of the model should be able to redraw the same background. A box with no width and a negative count are errors, not empty samples. The service calls this once per spatial block, then drops draws that land on ocean or on a presence cell.
""".strip()
