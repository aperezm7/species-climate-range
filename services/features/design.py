"""Presence-background design matrix on the climate grid."""

from __future__ import annotations

import math

import numpy as np

from src.background import sample_background
from src.blocks import block_edges
from src.grid import ClimateGrid, locate
from src.settings import Settings
from src.thin import thin_to_cell


def presence_bbox(records: list[dict], buffer_deg: float) -> tuple[float, float, float, float]:
    longitudes = [float(record["decimalLongitude"]) for record in records]
    latitudes = [float(record["decimalLatitude"]) for record in records]
    return (
        min(longitudes) - buffer_deg,
        min(latitudes) - buffer_deg,
        max(longitudes) + buffer_deg,
        max(latitudes) + buffer_deg,
    )


def modeling_bbox(records: list[dict]) -> tuple[float, float, float, float]:
    """Tight bbox of modeling presences. Blocks and background use this box."""
    longitudes = [float(record["decimalLongitude"]) for record in records]
    latitudes = [float(record["decimalLatitude"]) for record in records]
    return (min(longitudes), min(latitudes), max(longitudes), max(latitudes))


def thin_presences(records: list[dict], cell_size_deg: float) -> list[dict]:
    return thin_to_cell(records, cell_size_deg)


def cell_size_deg(grid: ClimateGrid) -> float:
    return abs(float(grid.transform.a))


def _cell(grid: ClimateGrid, longitude: float, latitude: float) -> tuple[int, int] | None:
    status, _values = locate(grid, longitude, latitude)
    if status != "ok":
        return None
    # locate already checked the index; recompute for the mask key.
    from rasterio.transform import rowcol

    row, col = rowcol(grid.transform, longitude, latitude, op=math.floor)
    return int(row), int(col)


def sample_background_on_grid(
    grid: ClimateGrid,
    bbox: tuple[float, float, float, float],
    presence_cells: set[tuple[int, int]],
    settings: Settings,
    target: int,
) -> list[dict]:
    """Stratified uniform background, skipping nodata and presence cells."""
    min_longitude, min_latitude, max_longitude, max_latitude = bbox
    lon_edges = block_edges(min_longitude, max_longitude, settings.n_lon_blocks)
    lat_edges = block_edges(min_latitude, max_latitude, settings.n_lat_blocks)
    kept: list[dict] = []
    seen = set(presence_cells)
    for batch in range(12):
        if len(kept) >= target:
            break
        for row in range(settings.n_lat_blocks):
            for col in range(settings.n_lon_blocks):
                if len(kept) >= target:
                    break
                lon0, lon1 = lon_edges[col], lon_edges[col + 1]
                lat0, lat1 = lat_edges[row], lat_edges[row + 1]
                pad_lon = max((lon1 - lon0) * 1e-6, 0)
                pad_lat = max((lat1 - lat0) * 1e-6, 0)
                draw = max(settings.background_per_block * 4, 20)
                seed = settings.random_seed + batch * 100 + row * settings.n_lon_blocks + col
                points = sample_background(
                    lon0 + pad_lon,
                    lat0 + pad_lat,
                    lon1 - pad_lon,
                    lat1 - pad_lat,
                    draw,
                    seed,
                )
                for point in points:
                    cell = _cell(grid, point["decimalLongitude"], point["decimalLatitude"])
                    if cell is None or cell in seen:
                        continue
                    seen.add(cell)
                    kept.append(point)
                    if len(kept) >= target:
                        break
    if len(kept) < 8:
        raise RuntimeError(
            f"only {len(kept)} background cells had climate data inside the bounding box"
        )
    return kept[:target]


def design_matrix(
    presences: list[dict],
    background: list[dict],
    grid: ClimateGrid,
) -> tuple[np.ndarray, np.ndarray, list[float], list[float]]:
    rows: list[list[float]] = []
    labels: list[int] = []
    latitudes: list[float] = []
    longitudes: list[float] = []
    for label, points in ((1, presences), (0, background)):
        for point in points:
            status, values = locate(
                grid, float(point["decimalLongitude"]), float(point["decimalLatitude"])
            )
            if status != "ok" or values is None:
                continue
            bio1, bio12 = values
            rows.append([bio1, bio12])
            labels.append(label)
            latitudes.append(float(point["decimalLatitude"]))
            longitudes.append(float(point["decimalLongitude"]))
    if not rows:
        raise RuntimeError("no points had climate values")
    return (
        np.asarray(rows, dtype="float64"),
        np.asarray(labels, dtype="int64"),
        latitudes,
        longitudes,
    )
