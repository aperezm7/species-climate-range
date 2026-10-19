# 01 — Validate a GBIF point

GBIF stores a missing coordinate in two ways: a null, or the pair `(0, 0)`, which lands in the Gulf of Guinea and is called null island. Both have to leave the occurrence table before a range model sees them.

Implement `validate_points(records)` in `starter.py`.

Each record is a dict with `decimalLatitude` and `decimalLongitude`. Values may be numbers, numeric strings, or missing (`None`, `""`, `"null"`, `"nan"`).

Keep a record only when both coordinates parse to finite numbers, the point is inside latitude `[-90, 90]` and longitude `[-180, 180]`, and the point is not exactly `(0, 0)`. Keep a point that sits on the equator or the prime meridian when the other coordinate is real. Keep extra keys, keep input order, and do not mutate the input list.

```python
records = [
    {"decimalLatitude": None, "decimalLongitude": -60, "gbifID": 1},
    {"decimalLatitude": 0, "decimalLongitude": 0, "gbifID": 2},
    {"decimalLatitude": 0, "decimalLongitude": -60.2, "gbifID": 3},
    {"decimalLatitude": -3.1, "decimalLongitude": -60.2, "gbifID": 4},
]
# ids 3 and 4 stay
```

Check your work with:

```bash
pytest challenges/01_validate_gbif_point
```
