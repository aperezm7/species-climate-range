"""Drop GBIF points that cannot be used as presences."""

from __future__ import annotations

from src.coords import parse_coordinate


def validate_points(records: list[dict]) -> list[dict]:
    """Keep records with a real latitude and longitude.

    A record is dropped when either coordinate is missing, when both are
    exactly 0 (GBIF's null island), or when the point lies outside the
    WGS84 ranges. A point on the equator or the prime meridian is kept
    when the other coordinate is real.
    """
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    kept: list[dict] = []
    for record in records:
        if not isinstance(record, dict):
            raise TypeError("each record must be a dict")
        latitude = parse_coordinate(record.get("decimalLatitude"))
        longitude = parse_coordinate(record.get("decimalLongitude"))
        if latitude is None or longitude is None:
            continue
        if latitude == 0 and longitude == 0:
            continue
        if not -90 <= latitude <= 90:
            continue
        if not -180 <= longitude <= 180:
            continue
        kept.append(record)
    return kept
