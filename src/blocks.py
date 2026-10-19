"""Spatial block cross-validation for presence-background models."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from sklearn.model_selection import GroupKFold, train_test_split

from src.metrics import roc_auc


def block_edges(start: float, stop: float, n_blocks: int) -> list[float]:
    if n_blocks < 1:
        raise ValueError("n_blocks must be at least 1")
    if stop < start:
        raise ValueError("stop must be greater than or equal to start")
    edges = [start + index * (stop - start) / n_blocks for index in range(n_blocks + 1)]
    edges[-1] = stop
    return edges


def block_index(value: float, edges: list[float]) -> int:
    """Bin value into a half-open interval. The last edge belongs to the last block."""
    n_blocks = len(edges) - 1
    if value >= edges[-1]:
        return n_blocks - 1
    index = 0
    for candidate in range(n_blocks):
        if value >= edges[candidate]:
            index = candidate
        else:
            break
    return index


def assign_block_ids(
    latitudes: list[float],
    longitudes: list[float],
    bbox: tuple[float, float, float, float],
    n_lat_blocks: int = 2,
    n_lon_blocks: int = 2,
) -> list[int]:
    """Block id for each point. bbox is (min_longitude, min_latitude, max_longitude, max_latitude)."""
    min_longitude, min_latitude, max_longitude, max_latitude = bbox
    lon_edges = block_edges(min_longitude, max_longitude, n_lon_blocks)
    lat_edges = block_edges(min_latitude, max_latitude, n_lat_blocks)
    ids: list[int] = []
    for latitude, longitude in zip(latitudes, longitudes):
        row = block_index(latitude, lat_edges)
        col = block_index(longitude, lon_edges)
        ids.append(row * n_lon_blocks + col)
    return ids


def spatial_block_auc(
    features: np.ndarray,
    labels: np.ndarray,
    latitudes: list[float],
    longitudes: list[float],
    bbox: tuple[float, float, float, float],
    estimator_factory: Callable[[], object],
    seed: int = 42,
    n_lat_blocks: int = 2,
    n_lon_blocks: int = 2,
) -> dict:
    """Mean ROC AUC across spatial blocks.

    Folds that do not contain both classes are skipped. When fewer than two
    spatial folds are usable, a stratified random holdout is reported instead
    and cv_mode is random_fallback.
    """
    groups = np.asarray(
        assign_block_ids(latitudes, longitudes, bbox, n_lat_blocks, n_lon_blocks)
    )
    y = np.asarray(labels).astype(int)
    fold_aucs: list[float] = []
    unique_groups = sorted(set(groups.tolist()))
    n_splits = min(4, len(unique_groups))
    if n_splits >= 2:
        splitter = GroupKFold(n_splits=n_splits)
        for train_index, test_index in splitter.split(features, y, groups):
            if len(set(y[train_index].tolist())) < 2 or len(set(y[test_index].tolist())) < 2:
                continue
            model = estimator_factory()
            model.fit(features[train_index], y[train_index])
            scores = model.predict_proba(features[test_index])[:, 1]
            fold_aucs.append(roc_auc(scores.tolist(), y[test_index].tolist()))
    if len(fold_aucs) >= 2:
        return {
            "spatial_block_auc": float(np.mean(fold_aucs)),
            "cv_mode": "spatial_block",
            "fold_aucs": [float(value) for value in fold_aucs],
        }
    features_train, features_test, y_train, y_test = train_test_split(
        features,
        y,
        test_size=0.3,
        random_state=seed,
        stratify=y,
    )
    model = estimator_factory()
    model.fit(features_train, y_train)
    scores = model.predict_proba(features_test)[:, 1]
    holdout = roc_auc(scores.tolist(), y_test.tolist())
    return {
        "spatial_block_auc": float(holdout),
        "cv_mode": "random_fallback",
        "fold_aucs": [float(holdout)],
    }
