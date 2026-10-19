# 05 — Count records per 1-degree cell

The occurrence table in Postgres is the sampling-effort map. One query should say how many stored rows sit in each 1-degree cell. That is coarser than the climate grid on purpose: it shows where GBIF is crowded, not where the model was thinned.

Implement `cell_count_sql()` so it returns one SQL string. The service runs that string against the `occurrences` table, which has `latitude` and `longitude` columns.

The result columns, in order, are:

- `lat_cell` — `FLOOR(latitude)`
- `lon_cell` — `FLOOR(longitude)`
- `n_records` — how many rows fall in that cell

Group by those cells and order by `lat_cell`, then `lon_cell`.

`FLOOR` goes toward negative infinity. Latitude `-3.2` is cell `-4`, because the cell is the half-open interval `[-4, -3)`. Longitude `-60.2` is cell `-61`. Truncating toward zero, or casting to integer, puts those South American points in the wrong cell.

`learn/sql.md` annotates the query the service runs. Read it after you have a version that passes, or when the floor direction stops making sense.

```bash
pytest challenges/05_cell_count_sql
```
