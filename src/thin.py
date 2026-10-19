"""One presence per climate-grid cell."""

from __future__ import annotations

import math

from src.coords import parse_coordinate


def thin_to_cell(records: list[dict], cell_size_deg: float) -> list[dict]:
    """Keep the first record in each grid cell.

    Cell index is floor(coordinate / cell_size_deg). Floor, not truncation
    toward zero, so negative longitudes in the Americas stay in the cell
    that contains them. Input order is preserved.
    """
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    if isinstance(cell_size_deg, bool) or not isinstance(cell_size_deg, (int, float)):
        raise TypeError("cell_size_deg must be a number")
    if not math.isfinite(cell_size_deg) or cell_size_deg <= 0:
        raise ValueError("cell_size_deg must be positive")
    seen: set[tuple[int, int]] = set()
    kept: list[dict] = []
    for record in records:
        if not isinstance(record, dict):
            raise TypeError("each record must be a dict")
        latitude = parse_coordinate(record.get("decimalLatitude"))
        longitude = parse_coordinate(record.get("decimalLongitude"))
        if latitude is None or longitude is None:
            raise ValueError("thin_to_cell expects coordinates; run validate_points first")
        key = (
            math.floor(latitude / cell_size_deg),
            math.floor(longitude / cell_size_deg),
        )
        if key in seen:
            continue
        seen.add(key)
        kept.append(record)
    return kept
