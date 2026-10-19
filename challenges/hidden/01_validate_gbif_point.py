import math


def _parse(value):
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


def validate_points(records: list[dict]) -> list[dict]:
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    kept = []
    for record in records:
        if not isinstance(record, dict):
            raise TypeError("each record must be a dict")
        latitude = _parse(record.get("decimalLatitude"))
        longitude = _parse(record.get("decimalLongitude"))
        if latitude is None or longitude is None:
            continue
        if latitude == 0 and longitude == 0:
            continue
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            continue
        kept.append(record)
    return kept


EXPLANATION = """
GBIF writes a missing coordinate as null, or as (0, 0). That second form is null island, in the Gulf of Guinea, and it will look like a real presence if you only drop nulls. A point with one coordinate at 0 is different: the equator and the prime meridian are real places, so (0, -60) stays.

The range check is the other half of validation. A latitude of 91 or a longitude of 181 is not a WGS84 point; it is usually a swapped pair or a projected coordinate that was never unprojected. Non-finite values (NaN, inf) fail the same test as null.
""".strip()
