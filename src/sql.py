"""Sampling-effort query for the occurrence table."""


def cell_count_sql() -> str:
    """Count occurrence rows in each 1-degree cell.

    FLOOR is toward negative infinity. In South America that puts longitude
    -60.2 in cell -61, the half-open interval [-61, -60). See learn/sql.md.
    """
    return """
SELECT
    FLOOR(latitude) AS lat_cell,
    FLOOR(longitude) AS lon_cell,
    COUNT(*) AS n_records
FROM occurrences
GROUP BY lat_cell, lon_cell
ORDER BY lat_cell, lon_cell
""".strip()
