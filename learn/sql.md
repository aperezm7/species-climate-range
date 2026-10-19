# Counting occurrences per 1-degree cell

Postgres holds the occurrence table. The model thins points to the climate grain before it fits. This query does not. It counts stored rows in each 1-degree cell so you can see where the GBIF search is crowded. A dataframe group-by would describe only the batch this process had loaded. The table is the record, including rows inserted by a later load, so the count belongs in SQL.

The service runs the string returned by `cell_count_sql()` in `src/sql.py`:

```sql
SELECT
    FLOOR(latitude) AS lat_cell,
    FLOOR(longitude) AS lon_cell,
    COUNT(*) AS n_records
FROM occurrences
GROUP BY lat_cell, lon_cell
ORDER BY lat_cell, lon_cell
```

`GET /cells` returns that result after the gateway has loaded the validated occurrences.

## What each line is doing

`FROM occurrences` reads the table created in `services/data/schema.sql`. Columns used here are `latitude` and `longitude`. The scientific name is not in the `GROUP BY` because a run truncates the table and loads one species.

`FLOOR(latitude)` and `FLOOR(longitude)` assign the 1-degree cell. The cell is the half-open interval `[n, n+1)`. The label stored in `lat_cell` or `lon_cell` is `n`, the floor of the coordinate.

`COUNT(*)` is the number of rows in that cell, not the number of thinned presences. Two jaguar records 10 km apart in the same degree cell count as two. The model may later keep only one of them.

`GROUP BY lat_cell, lon_cell` collapses the table to one row per cell. Postgres accepts the select-list aliases here.

`ORDER BY lat_cell, lon_cell` makes the map stable from run to run. South to north, then west to east, because floor labels increase in that direction.

## Floor and the Americas

`FLOOR` goes toward negative infinity. Truncation toward zero, including a cast to integer, does not.

Take four points:

| latitude | longitude | lat_cell | lon_cell |
| --- | --- | --- | --- |
| -3.2 | -60.2 | -4 | -61 |
| -3.8 | -60.9 | -4 | -61 |
| -3.1 | -61.0 | -4 | -61 |
| 0.2 | -59.1 | 0 | -60 |

Latitude `-3.2` is not in cell `-3`. It is just south of `-3`, inside `[-4, -3)`, so the cell is `-4`. The same three latitudes all fall in `-4`. Longitude `-60.2` is inside `[-61, -60)`, and so is the edge `-61.0`. They share `lon_cell = -61`. The point at longitude `-59.1` is the next cell east.

The query therefore returns two rows: `(-4, -61, 3)` and `(0, -60, 1)`.

A cast to integer would report latitude cell `-3` for the first three points and longitude cell `-60` for `-60.2`. Every cell in South America would shift. That is why the SQL uses `FLOOR`.
