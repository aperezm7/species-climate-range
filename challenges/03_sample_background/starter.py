# Complete the functions below. Do not change the signatures.


def sample_background(
    min_longitude: float,
    min_latitude: float,
    max_longitude: float,
    max_latitude: float,
    n: int,
    seed: int,
) -> list[dict]:
    """Draw background points inside a bounding box."""
    # GBIF gives presences, not absences. A presence-background model needs
    # contrast points inside the region you are willing to treat as the
    # domain. The simple domain sample is a uniform draw inside the bounding
    # box of the presences.
    #
    # Steps:
    # - Draw n points uniformly inside the closed box
    #   [min_longitude, max_longitude] by [min_latitude, max_latitude].
    # - Seed the draw so the same seed returns the same points.
    #
    # Edge cases:
    # - n = 0 returns an empty list.
    # - A negative n raises ValueError.
    # - A box with no width or no height raises ValueError.
    # - The draw is uniform in degrees, not equal-area. Do not reproject.
    #
    # Return value: a list of n dicts, each with decimalLongitude and
    # decimalLatitude. Every point must fall inside the closed box.
    raise NotImplementedError
