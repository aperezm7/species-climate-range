"""Fit a presence-background gradient boosting model and write a suitability GeoTIFF."""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass

import joblib
import numpy as np
from rasterio.transform import rowcol
from sklearn.ensemble import GradientBoostingClassifier

from services.data.climate import download_worldclim
from services.data.fixtures import load_fixture_grid
from services.data.occurrences import load_occurrence_rows, prepare_records
from services.features.design import (
    cell_size_deg,
    design_matrix,
    modeling_bbox,
    presence_bbox,
    sample_background_on_grid,
    thin_presences,
)
from src.blocks import spatial_block_auc
from src.grid import NODATA, ClimateGrid, crop_pair, locate, write_band
from src.settings import Settings, load_settings

logger = logging.getLogger("species.model")


@dataclass
class Artifact:
    model: GradientBoostingClassifier
    grid: ClimateGrid
    suitability_path: object
    metrics: dict
    occurrences: list[dict]
    settings: Settings


def make_estimator() -> GradientBoostingClassifier:
    return GradientBoostingClassifier(
        n_estimators=60,
        learning_rate=0.1,
        max_depth=2,
        random_state=42,
    )


def train(settings: Settings | None = None) -> Artifact:
    settings = settings or load_settings()
    settings.artifact_dir.mkdir(parents=True, exist_ok=True)
    raw_rows = load_occurrence_rows(settings)
    occurrences = prepare_records(raw_rows, settings.scientific_name)
    if len(occurrences) < 8:
        raise RuntimeError(
            f"only {len(occurrences)} usable occurrences for {settings.scientific_name}"
        )
    logger.info(
        "occurrences raw=%s usable=%s mode=%s",
        len(raw_rows),
        len(occurrences),
        settings.data_mode,
    )
    crop_bounds = presence_bbox(occurrences, settings.bbox_buffer_deg)
    if settings.data_mode == "fixture":
        source_dir = settings.artifact_dir / "fixture_source"
        bio1_path, bio12_path, _source = load_fixture_grid(
            settings.fixture_dir / "climate_grid.csv", source_dir
        )
        worldclim = False
    else:
        bio1_path, bio12_path = download_worldclim(settings.cache_dir / "worldclim")
        worldclim = True
    grid = crop_pair(
        bio1_path,
        bio12_path,
        crop_bounds,
        settings.artifact_dir,
        worldclim=worldclim,
    )
    thinned = thin_presences(occurrences, cell_size_deg(grid))
    presences = []
    presence_cells: set[tuple[int, int]] = set()
    for record in thinned:
        status, _values = locate(grid, record["decimalLongitude"], record["decimalLatitude"])
        if status != "ok":
            continue
        row, col = rowcol(
            grid.transform, record["decimalLongitude"], record["decimalLatitude"], op=math.floor
        )
        cell = (int(row), int(col))
        if cell in presence_cells:
            continue
        presence_cells.add(cell)
        presences.append(record)
    if len(presences) < 8:
        raise RuntimeError(f"only {len(presences)} presences fell on climate cells")
    bbox = modeling_bbox(presences)
    n_blocks = settings.n_lat_blocks * settings.n_lon_blocks
    target_background = min(4000, max(settings.background_per_block * n_blocks, len(presences)))
    background = sample_background_on_grid(
        grid, bbox, presence_cells, settings, target_background
    )
    features, labels, latitudes, longitudes = design_matrix(presences, background, grid)
    if len(set(labels.tolist())) < 2:
        raise RuntimeError("the design matrix has only one class")
    evaluation = spatial_block_auc(
        features,
        labels,
        latitudes,
        longitudes,
        bbox,
        make_estimator,
        seed=settings.random_seed,
        n_lat_blocks=settings.n_lat_blocks,
        n_lon_blocks=settings.n_lon_blocks,
    )
    model = make_estimator()
    model.fit(features, labels)
    suitability = _suitability_surface(model, grid)
    suitability_path = settings.artifact_dir / "suitability.tif"
    write_band(suitability_path, suitability, grid.transform, grid.crs, NODATA)
    metrics = {
        "scientific_name": settings.scientific_name,
        "common_name": settings.common_name,
        "data_mode": settings.data_mode,
        "n_raw": len(raw_rows),
        "n_occurrence_rows": len(occurrences),
        "n_presence": int(len(presences)),
        "n_background": int((labels == 0).sum()),
        "spatial_block_auc": evaluation["spatial_block_auc"],
        "cv_mode": evaluation["cv_mode"],
        "fold_aucs": evaluation["fold_aucs"],
        "bbox": {
            "min_longitude": bbox[0],
            "min_latitude": bbox[1],
            "max_longitude": bbox[2],
            "max_latitude": bbox[3],
        },
    }
    (settings.artifact_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    joblib.dump({"model": model, "feature_names": ["bio1", "bio12"]}, settings.artifact_dir / "model.joblib")
    logger.info(
        "trained presences=%s background=%s auc=%.3f mode=%s",
        metrics["n_presence"],
        metrics["n_background"],
        metrics["spatial_block_auc"],
        metrics["cv_mode"],
    )
    return Artifact(
        model=model,
        grid=grid,
        suitability_path=suitability_path,
        metrics=metrics,
        occurrences=occurrences,
        settings=settings,
    )


def _suitability_surface(model: GradientBoostingClassifier, grid: ClimateGrid) -> np.ndarray:
    valid = (
        np.isfinite(grid.bio1)
        & np.isfinite(grid.bio12)
        & (grid.bio1 != grid.nodata)
        & (grid.bio12 != grid.nodata)
    )
    surface = np.full(grid.bio1.shape, NODATA, dtype="float32")
    if not valid.any():
        return surface
    features = np.column_stack([grid.bio1[valid], grid.bio12[valid]]).astype("float64")
    scores = model.predict_proba(features)[:, 1].astype("float32")
    surface[valid] = scores
    return surface


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = load_settings()
    artifact = train(settings)
    if settings.database_url:
        from services.data.db import replace_occurrences

        replace_occurrences(settings.database_url, artifact.occurrences)
        logger.info("loaded %s occurrences into Postgres", len(artifact.occurrences))
    print(json.dumps(artifact.metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
