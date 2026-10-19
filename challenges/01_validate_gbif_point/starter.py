# Complete the functions below. Do not change the signatures.


def validate_points(records: list[dict]) -> list[dict]:
    """Return the GBIF records that are usable points."""
    # GBIF stores a missing coordinate in two ways: a null, or the pair (0, 0),
    # which lands in the Gulf of Guinea and is called null island. Both have to
    # leave the occurrence table before a range model sees them.
    #
    # Each record is a dict with decimalLatitude and decimalLongitude. Values
    # may be numbers, numeric strings, or missing (None, "", "null", "nan").
    #
    # Steps:
    # - Walk the records in input order.
    # - Parse both coordinates. Keep a record only when both parse to finite
    #   numbers, the point is inside latitude [-90, 90] and longitude
    #   [-180, 180], and the point is not exactly (0, 0).
    #
    # Edge cases:
    # - Keep a point that sits on the equator or the prime meridian when the
    #   other coordinate is real. (0, -60.2) stays; (0, 0) does not.
    # - Drop a null latitude or longitude, an empty string, "null", "nan",
    #   and any non-finite value.
    # - Drop latitude 91 and longitude 181.
    # - Keep extra keys. Do not mutate the input list.
    #
    # Return value: the kept records, in input order. An empty input returns
    # an empty list.
    #
    # Example: ids 1 (null latitude) and 2 (null island) drop; ids 3
    # (0, -60.2) and 4 (-3.1, -60.2) stay.
    raise NotImplementedError
