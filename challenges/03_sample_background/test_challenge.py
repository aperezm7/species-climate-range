import pytest

from challenges.loader import load_challenge


def _mod():
    return load_challenge("03_sample_background")


def test_points_stay_inside_and_honor_the_seed():
    kwargs = dict(
        min_longitude=-70,
        min_latitude=-15,
        max_longitude=-50,
        max_latitude=5,
        n=20,
        seed=7,
    )
    first = _mod().sample_background(**kwargs)
    second = _mod().sample_background(**kwargs)
    assert first == second
    assert len(first) == 20
    for point in first:
        assert -70 <= point["decimalLongitude"] <= -50
        assert -15 <= point["decimalLatitude"] <= 5
    other = _mod().sample_background(**{**kwargs, "seed": 8})
    assert other != first


def test_empty_draw_and_rejected_boxes():
    mod = _mod()
    assert mod.sample_background(-1, -1, 1, 1, 0, 1) == []
    with pytest.raises(ValueError):
        mod.sample_background(10, -1, 0, 1, 3, 1)
    with pytest.raises(ValueError):
        mod.sample_background(0, 0, 1, 1, -1, 1)
    with pytest.raises(ValueError):
        mod.sample_background(0, 0, 0, 1, 3, 1)
