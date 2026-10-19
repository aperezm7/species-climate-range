# 03 — Sample background points

GBIF gives presences, not absences. A presence-background model needs contrast points inside the region you are willing to treat as the domain. The simple domain sample is a uniform draw inside the bounding box of the presences.

Implement `sample_background(min_longitude, min_latitude, max_longitude, max_latitude, n, seed)`.

Return `n` dicts with `decimalLongitude` and `decimalLatitude`. Every point must fall inside the closed box. The same seed must return the same points. `n = 0` returns an empty list. A negative `n`, or a box with no width or no height, raises `ValueError`.

The draw is uniform in degrees, not equal-area. Say so if you document the function; do not reproject.

```bash
pytest challenges/03_sample_background
```
