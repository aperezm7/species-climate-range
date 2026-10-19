import pytest

from challenges.loader import load_challenge


def _mod():
    return load_challenge("02_spatial_thinning")


def test_negative_longitudes_share_a_cell_until_the_next_boundary():
    records = [
        {"decimalLatitude": -3.2, "decimalLongitude": -60.2, "id": "a"},
        {"decimalLatitude": -3.8, "decimalLongitude": -60.9, "id": "b"},
        {"decimalLatitude": -3.1, "decimalLongitude": -61.2, "id": "c"},
        {"decimalLatitude": -3.4, "decimalLongitude": -61.0, "id": "d"},
    ]
    kept = _mod().thin_to_cell(records, 1)
    assert [row["id"] for row in kept] == ["a", "c"]


def test_half_degree_cells_split_a_one_degree_pair():
    records = [
        {"decimalLatitude": 10.1, "decimalLongitude": 20.1, "id": "a"},
        {"decimalLatitude": 10.6, "decimalLongitude": 20.1, "id": "b"},
    ]
    assert [row["id"] for row in _mod().thin_to_cell(records, 0.5)] == ["a", "b"]


def test_missing_coordinate_and_bad_cell_size():
    with pytest.raises(ValueError):
        _mod().thin_to_cell([{"decimalLatitude": None, "decimalLongitude": 1}], 1)
    with pytest.raises(ValueError):
        _mod().thin_to_cell([], 0)
