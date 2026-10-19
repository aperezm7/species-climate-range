"""Score one coordinate on a fitted suitability model."""

from __future__ import annotations

from services.model.train import Artifact
from src.grid import locate


def score_point(artifact: Artifact, latitude: float, longitude: float) -> dict:
    status, values = locate(artifact.grid, longitude, latitude)
    if status == "outside":
        raise LookupError("Point is outside the modeled extent.")
    if status != "ok" or values is None:
        raise LookupError("No climate value at this location.")
    bio1, bio12 = values
    suitability = float(artifact.model.predict_proba([[bio1, bio12]])[0, 1])
    metrics = artifact.metrics
    return {
        "scientific_name": artifact.settings.scientific_name,
        "common_name": artifact.settings.common_name,
        "latitude": latitude,
        "longitude": longitude,
        "bio1_celsius": bio1,
        "bio12_mm": bio12,
        "suitability": suitability,
        "spatial_block_auc": metrics["spatial_block_auc"],
        "cv_mode": metrics["cv_mode"],
        "n_presence": metrics["n_presence"],
        "n_background": metrics["n_background"],
        "data_mode": artifact.settings.data_mode,
    }
