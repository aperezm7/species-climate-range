def cell_count_sql() -> str:
    return """
SELECT
    FLOOR(latitude) AS lat_cell,
    FLOOR(longitude) AS lon_cell,
    COUNT(*) AS n_records
FROM occurrences
GROUP BY lat_cell, lon_cell
ORDER BY lat_cell, lon_cell
""".strip()


EXPLANATION = """
This is the sampling-effort map, not the model grain. One degree is coarse enough to show where GBIF rows pile up. The occurrence table is in Postgres, so the count stays correct when another client inserts a row; a dataframe group-by would only see the rows this process had loaded.

FLOOR goes toward negative infinity. Latitude -3.2 is not cell -3. It sits in the half-open interval [-4, -3), so the cell is -4. Longitude -60.2 is cell -61. Casting to integer truncates toward zero and shifts every cell in South America. learn/sql.md walks the same query with those numbers.
""".strip()
