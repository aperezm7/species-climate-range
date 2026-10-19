# 02 — Spatial thinning

Repeated records in the same climate cell inflate sample size and let the same cell sit in both sides of a spatial cross-validation split. Thin the table to one record per cell before fitting.

Implement `thin_to_cell(records, cell_size_deg)` in `starter.py`.

The cell index is `floor(coordinate / cell_size_deg)` for latitude and for longitude. Use floor toward negative infinity, not truncation toward zero. Longitude `-60.2` and longitude `-61.0` are the same 1-degree cell (`[-61, -60)`). Longitude `-61.2` is the next cell west.

Keep the first record in input order. Assume coordinates are already valid; if a coordinate is missing, raise `ValueError`. Reject a non-positive cell size.

```python
records = [
    {"decimalLatitude": -3.2, "decimalLongitude": -60.2, "id": "a"},
    {"decimalLatitude": -3.8, "decimalLongitude": -60.9, "id": "b"},
    {"decimalLatitude": -3.1, "decimalLongitude": -61.2, "id": "c"},
]
# cell size 1 keeps a and c
```

```bash
pytest challenges/02_spatial_thinning
```
