# Complete the functions below. Do not change the signatures.


def cell_count_sql() -> str:
    """Return the SQL that counts occurrence rows per 1-degree cell.

    The annotated version of this query is in learn/sql.md.
    """
    # The occurrence table is the sampling-effort map. One query should say
    # how many stored rows sit in each 1-degree cell. That is coarser than
    # the climate grid on purpose: it shows where GBIF is crowded, not where
    # the model was thinned.
    #
    # The service runs the string you return against the occurrences table,
    # which has latitude and longitude columns.
    #
    # Steps — result columns, in order:
    # - lat_cell is FLOOR(latitude)
    # - lon_cell is FLOOR(longitude)
    # - n_records is how many rows fall in that cell
    # - Group by those cells and order by lat_cell, then lon_cell.
    #
    # Edge cases:
    # - FLOOR goes toward negative infinity.
    # - Latitude -3.2 is cell -4, because the cell is the half-open interval
    #   [-4, -3). Longitude -60.2 is cell -61.
    # - Truncating toward zero, or casting to integer, puts those South
    #   American points in the wrong cell.
    #
    # Return value: one SQL string.
    #
    # Unfinished query (fill in the blanks, then return the string):
    # SELECT
    #     <floor of latitude> AS lat_cell,
    #     <floor of longitude> AS lon_cell,
    #     <row count> AS n_records
    # FROM <table>
    # GROUP BY <cells>
    # ORDER BY <cells>
    raise NotImplementedError
