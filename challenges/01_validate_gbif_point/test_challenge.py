import pytest

from challenges.loader import load_challenge


def _mod():
    return load_challenge("01_validate_gbif_point")


def test_drops_nulls_null_island_and_impossible_coordinates():
    records = [
        {"decimalLatitude": None, "decimalLongitude": -60.0, "gbifID": 1},
        {"decimalLatitude": -3.0, "decimalLongitude": None, "gbifID": 2},
        {"decimalLatitude": 0, "decimalLongitude": 0, "gbifID": 3},
        {"decimalLatitude": 0.0, "decimalLongitude": -0.0, "gbifID": 4},
        {"decimalLatitude": 0, "decimalLongitude": -60.2, "gbifID": 5},
        {"decimalLatitude": -3.1, "decimalLongitude": -60.2, "gbifID": 6},
        {"decimalLatitude": 91, "decimalLongitude": 10, "gbifID": 7},
        {"decimalLatitude": -3, "decimalLongitude": 181, "gbifID": 8},
        {"decimalLatitude": "nan", "decimalLongitude": -60, "gbifID": 9},
        {"decimalLatitude": "", "decimalLongitude": -60, "gbifID": 10},
        {"decimalLatitude": "-12.5", "decimalLongitude": "-50.25", "gbifID": 11},
        {"decimalLatitude": True, "decimalLongitude": -60, "gbifID": 12},
    ]
    kept = _mod().validate_points(records)
    assert [row["gbifID"] for row in kept] == [5, 6, 11]
    assert len(records) == 12


def test_empty_input():
    assert _mod().validate_points([]) == []


def test_rejects_a_non_list():
    with pytest.raises(TypeError):
        _mod().validate_points({"decimalLatitude": 1, "decimalLongitude": 2})
