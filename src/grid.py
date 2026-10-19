"""Read and write the climate and suitability grids."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import array_bounds, from_origin, rowcol
from rasterio.windows import Window, from_bounds

NODATA = -9999.0


@dataclass
class ClimateGrid:
    bio1: np.ndarray
    bio12: np.ndarray
    transform: rasterio.Affine
    crs: str
    nodata: float

    @property
    def height(self) -> int:
        return int(self.bio1.shape[0])

    @property
    def width(self) -> int:
        return int(self.bio1.shape[1])

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        left, bottom, right, top = array_bounds(self.height, self.width, self.transform)
        return float(left), float(bottom), float(right), float(top)


def write_band(
    path: Path,
    values: np.ndarray,
    transform: rasterio.Affine,
    crs: str = "EPSG:4326",
    nodata: float = NODATA,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff",
        "height": values.shape[0],
        "width": values.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
        "compress": "deflate",
    }
    with rasterio.open(path, "w", **profile) as dataset:
        dataset.write(values.astype("float32"), 1)


def temperature_scale(raw: np.ndarray, nodata: object) -> float:
    """Return 0.1 when a WorldClim grid is stored as °C × 10, else 1.

    The 10-arc-minute float GeoTIFFs from geodata.ucdavis.edu are already in
    °C (annual means stay near -55 to 31). Older integer grids store tenths
    of a degree, and those values exceed 80 away from a narrow temperate band.
    """
    data = raw.astype("float64")
    valid = np.isfinite(data)
    if nodata is not None:
        try:
            nodata_value = float(nodata)
        except (TypeError, ValueError):
            nodata_value = None
        if nodata_value is not None and math.isfinite(nodata_value):
            valid = valid & (data != nodata_value)
    valid = valid & (data > -1000)
    if not np.any(valid):
        return 1.0
    peak = float(np.max(np.abs(data[valid])))
    if peak > 80.0:
        return 0.1
    return 1.0


def scale_band(raw: np.ndarray, nodata: object, worldclim: bool, scale: float) -> np.ndarray:
    """Mask nodata and, for official WorldClim files, convert BIO1 from °C * 10."""
    data = raw.astype("float32")
    mask = ~np.isfinite(data)
    if nodata is not None:
        try:
            nodata_value = float(nodata)
        except (TypeError, ValueError):
            nodata_value = None
        if nodata_value is not None and math.isfinite(nodata_value):
            mask = mask | (raw == nodata)
    if worldclim:
        mask = mask | (data < -1000)
    scaled = np.full(data.shape, NODATA, dtype="float32")
    valid = ~mask
    scaled[valid] = data[valid] * np.float32(scale)
    return scaled


def crop_pair(
    bio1_path: Path,
    bio12_path: Path,
    bounds: tuple[float, float, float, float],
    dest_dir: Path,
    worldclim: bool,
) -> ClimateGrid:
    """Crop BIO1 and BIO12 to bounds and return them in real units on one grid."""
    min_longitude, min_latitude, max_longitude, max_latitude = bounds
    with rasterio.open(bio1_path) as src1, rasterio.open(bio12_path) as src2:
        if src1.width != src2.width or src1.height != src2.height or src1.transform != src2.transform:
            raise RuntimeError("BIO1 and BIO12 are not on the same grid")
        window = from_bounds(
            min_longitude, min_latitude, max_longitude, max_latitude, src1.transform
        )
        # Cover every pixel the box touches. Rounding the length alone drops
        # the partial pixel on the far edge.
        col_off = math.floor(window.col_off)
        row_off = math.floor(window.row_off)
        col_end = math.ceil(window.col_off + window.width)
        row_end = math.ceil(window.row_off + window.height)
        window = Window(col_off, row_off, col_end - col_off, row_end - row_off)
        window = window.intersection(Window(0, 0, src1.width, src1.height))
        if window.width <= 0 or window.height <= 0:
            raise RuntimeError("bounding box does not overlap the climate grid")
        raw1 = src1.read(1, window=window)
        raw2 = src2.read(1, window=window)
        transform = src1.window_transform(window)
        crs = src1.crs.to_string() if src1.crs else "EPSG:4326"
        nodata1 = src1.nodata
        nodata2 = src2.nodata
    bio1_scale = temperature_scale(raw1, nodata1) if worldclim else 1.0
    bio1 = scale_band(raw1, nodata1, worldclim, bio1_scale)
    bio12 = scale_band(raw2, nodata2, worldclim, 1.0)
    dest_dir.mkdir(parents=True, exist_ok=True)
    write_band(dest_dir / "bio1_crop.tif", bio1, transform, crs)
    write_band(dest_dir / "bio12_crop.tif", bio12, transform, crs)
    return ClimateGrid(bio1=bio1, bio12=bio12, transform=transform, crs=crs, nodata=NODATA)


def locate(
    grid: ClimateGrid, longitude: float, latitude: float
) -> tuple[str, tuple[float, float] | None]:
    """Return ('ok', (bio1, bio12)), ('nodata', None), or ('outside', None)."""
    row, col = rowcol(grid.transform, longitude, latitude, op=math.floor)
    if row < 0 or col < 0 or row >= grid.height or col >= grid.width:
        return "outside", None
    bio1 = float(grid.bio1[row, col])
    bio12 = float(grid.bio12[row, col])
    if (
        not math.isfinite(bio1)
        or not math.isfinite(bio12)
        or bio1 == grid.nodata
        or bio12 == grid.nodata
    ):
        return "nodata", None
    return "ok", (bio1, bio12)


def grid_from_points(
    longitudes: list[float],
    latitudes: list[float],
    bio1_values: list[float | None],
    bio12_values: list[float | None],
) -> ClimateGrid:
    """Build a regular lon/lat grid. None values are nodata."""
    unique_lons = sorted(set(longitudes))
    unique_lats = sorted(set(latitudes))
    if len(unique_lons) < 2 or len(unique_lats) < 2:
        raise ValueError("climate grid needs at least a 2 by 2 set of cells")
    res_x = unique_lons[1] - unique_lons[0]
    res_y = unique_lats[1] - unique_lats[0]
    if res_x <= 0 or res_y <= 0:
        raise ValueError("climate coordinates must increase")
    for left, right in zip(unique_lons, unique_lons[1:]):
        if abs((right - left) - res_x) > 1e-6:
            raise ValueError("longitude spacing is not regular")
    for bottom, top in zip(unique_lats, unique_lats[1:]):
        if abs((top - bottom) - res_y) > 1e-6:
            raise ValueError("latitude spacing is not regular")
    west = unique_lons[0] - res_x / 2
    north = unique_lats[-1] + res_y / 2
    transform = from_origin(west, north, res_x, res_y)
    height = len(unique_lats)
    width = len(unique_lons)
    bio1 = np.full((height, width), NODATA, dtype="float32")
    bio12 = np.full((height, width), NODATA, dtype="float32")
    for longitude, latitude, value1, value12 in zip(
        longitudes, latitudes, bio1_values, bio12_values
    ):
        if value1 is None or value12 is None:
            continue
        if not math.isfinite(value1) or not math.isfinite(value12):
            continue
        row, col = rowcol(transform, longitude, latitude, op=math.floor)
        if row < 0 or col < 0 or row >= height or col >= width:
            raise ValueError(f"point {(latitude, longitude)} fell outside the fixture grid")
        bio1[row, col] = value1
        bio12[row, col] = value12
    return ClimateGrid(bio1=bio1, bio12=bio12, transform=transform, crs="EPSG:4326", nodata=NODATA)
