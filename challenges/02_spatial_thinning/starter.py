# Complete the functions below. Do not change the signatures.


def thin_to_cell(records: list[dict], cell_size_deg: float) -> list[dict]:
    """Keep one record per grid cell."""
    # Repeated records in the same climate cell inflate sample size and let
    # the same cell sit in both sides of a spatial cross-validation split.
    # Thin the table to one record per cell before fitting.
    #
    # Steps:
    # - The cell index is floor(coordinate / cell_size_deg) for latitude and
    #   for longitude.
    # - Use floor toward negative infinity, not truncation toward zero.
    # - Keep the first record in input order for each cell.
    #
    # Edge cases:
    # - Longitude -60.2 and longitude -61.0 are the same 1-degree cell
    #   ([-61, -60)). Longitude -61.2 is the next cell west.
    # - Assume coordinates are already valid. If a coordinate is missing,
    #   raise ValueError.
    # - Reject a non-positive cell size.
    #
    # Return value: the kept records, in input order. For the sample below
    # with cell size 1, keep ids "a" and "c":
    #   a (-3.2, -60.2), b (-3.8, -60.9), c (-3.1, -61.2).
    raise NotImplementedError
