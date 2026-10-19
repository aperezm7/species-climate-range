"""Build GeoTIFFs from the committed climate grid."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from src.grid import NODATA, ClimateGrid, grid_from_points, write_band


def load_fixture_grid(csv_path: Path, dest_dir: Path) -> tuple[Path, Path, ClimateGrid]:
    frame = pd.read_csv(csv_path)
    longitudes = [float(value) for value in frame["longitude"]]
    latitudes = [float(value) for value in frame["latitude"]]
    bio1_values = [_optional_float(value) for value in frame["bio1"]]
    bio12_values = [_optional_float(value) for value in frame["bio12"]]
    grid = grid_from_points(longitudes, latitudes, bio1_values, bio12_values)
    dest_dir.mkdir(parents=True, exist_ok=True)
    bio1_path = dest_dir / "fixture_bio1.tif"
    bio12_path = dest_dir / "fixture_bio12.tif"
    write_band(bio1_path, grid.bio1, grid.transform, grid.crs, NODATA)
    write_band(bio12_path, grid.bio12, grid.transform, grid.crs, NODATA)
    return bio1_path, bio12_path, grid


def _optional_float(value: object) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    if pd.isna(value):
        return None
    return float(value)
