"""The service algorithms and the revealed solutions agree on the contract cases."""

import importlib.util
from pathlib import Path

from src.background import sample_background
from src.metrics import roc_auc
from src.sql import cell_count_sql
from src.thin import thin_to_cell
from src.validate import validate_points

HIDDEN = Path(__file__).resolve().parents[1] / "challenges" / "hidden"


def _hidden(slug: str):
    path = HIDDEN / f"{slug}.py"
    spec = importlib.util.spec_from_file_location(f"hidden_{slug}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validation_matches():
    records = [
        {"decimalLatitude": None, "decimalLongitude": 1, "gbifID": 1},
        {"decimalLatitude": 0, "decimalLongitude": 0, "gbifID": 2},
        {"decimalLatitude": -12.5, "decimalLongitude": -60, "gbifID": 3},
    ]
    hidden = _hidden("01_validate_gbif_point").validate_points(records)
    assert [row["gbifID"] for row in hidden] == [row["gbifID"] for row in validate_points(records)]


def test_thinning_matches():
    records = [
        {"decimalLatitude": -3.2, "decimalLongitude": -60.2, "id": "a"},
        {"decimalLatitude": -3.8, "decimalLongitude": -60.9, "id": "b"},
        {"decimalLatitude": -3.1, "decimalLongitude": -61.2, "id": "c"},
    ]
    hidden = _hidden("02_spatial_thinning").thin_to_cell(records, 1)
    assert [row["id"] for row in hidden] == [row["id"] for row in thin_to_cell(records, 1)]


def test_background_matches():
    args = (-80, -20, -40, 10, 6, 3)
    hidden = _hidden("03_sample_background").sample_background(*args)
    assert hidden == sample_background(*args)


def test_auc_matches():
    scores = [0.2, 0.4, 0.4, 0.9]
    labels = [0, 0, 1, 1]
    hidden = _hidden("04_roc_auc").roc_auc(scores, labels)
    assert hidden == roc_auc(scores, labels)


def test_sql_matches():
    assert _hidden("05_cell_count_sql").cell_count_sql() == cell_count_sql()
