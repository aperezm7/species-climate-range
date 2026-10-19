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


def thin_to_cell(records: list[dict], cell_size_deg: float) -> list[dict]:
    if not isinstance(records, list):
        raise TypeError("records must be a list")
    if isinstance(cell_size_deg, bool) or not isinstance(cell_size_deg, (int, float)):
        raise TypeError("cell_size_deg must be a number")
    if not math.isfinite(float(cell_size_deg)) or cell_size_deg <= 0:
        raise ValueError("cell_size_deg must be positive")
    seen = set()
    kept = []
    for record in records:
        if not isinstance(record, dict):
            raise TypeError("each record must be a dict")
        latitude = _parse(record.get("decimalLatitude"))
        longitude = _parse(record.get("decimalLongitude"))
        if latitude is None or longitude is None:
            raise ValueError("thin_to_cell expects coordinates; run validate_points first")
        key = (math.floor(latitude / cell_size_deg), math.floor(longitude / cell_size_deg))
        if key in seen:
            continue
        seen.add(key)
        kept.append(record)
    return kept


EXPLANATION = """
Several GBIF rows can fall in one climate cell. If you keep them all, that cell is counted many times and can land in both the training block and the test block.

The cell is floor(coordinate / cell_size). Floor goes toward negative infinity. Truncating toward zero is wrong in the Americas: int(-60.2) is -60, but the 1-degree cell that contains -60.2 is [-61, -60), so the index is -61. The same rule puts -61.0 in that cell and -61.2 in the next cell west.

Keeping the first row in input order makes the thinning deterministic. Any later row in that cell is a duplicate for this model, not extra evidence.
""".strip()
