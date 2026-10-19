"""HTTP API for climatic suitability."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from services.model.score import score_point
from services.model.train import Artifact, train
from src.settings import load_settings

QUESTION = "Where is climatic suitability highest for a focal species?"


class SuitabilityRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, examples=[-14.0])
    longitude: float = Field(..., ge=-180, le=180, examples=[-68.0])


class SuitabilityResponse(BaseModel):
    scientific_name: str
    common_name: str
    latitude: float
    longitude: float
    bio1_celsius: float
    bio12_mm: float
    suitability: float
    spatial_block_auc: float
    cv_mode: str
    n_presence: int
    n_background: int
    data_mode: str


class CellCount(BaseModel):
    lat_cell: int
    lon_cell: int
    n_records: int


class CellsResponse(BaseModel):
    cell_size_degrees: int
    cells: list[CellCount]


def _artifact() -> Artifact:
    artifact = getattr(app.state, "artifact", None)
    if artifact is None:
        raise HTTPException(status_code=503, detail="Model is not ready.")
    return artifact


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    artifact = train(settings)
    if settings.database_url:
        from services.data.db import replace_occurrences

        replace_occurrences(settings.database_url, artifact.occurrences)
    app.state.artifact = artifact
    yield


app = FastAPI(
    title="Species climate range",
    summary=QUESTION,
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def root() -> dict:
    artifact = getattr(app.state, "artifact", None)
    species = artifact.settings.scientific_name if artifact else None
    return {
        "question": QUESTION,
        "scientific_name": species,
        "endpoints": {
            "health": "/health",
            "suitability": "POST /suitability",
            "map": "GET /map",
            "cells": "GET /cells",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health() -> dict:
    artifact = _artifact()
    left, bottom, right, top = artifact.grid.bounds
    return {
        "status": "ok",
        "scientific_name": artifact.settings.scientific_name,
        "common_name": artifact.settings.common_name,
        "data_mode": artifact.settings.data_mode,
        "model_ready": True,
        "spatial_block_auc": artifact.metrics["spatial_block_auc"],
        "cv_mode": artifact.metrics["cv_mode"],
        "n_presence": artifact.metrics["n_presence"],
        "n_background": artifact.metrics["n_background"],
        "bbox": {
            "min_longitude": left,
            "min_latitude": bottom,
            "max_longitude": right,
            "max_latitude": top,
        },
    }


@app.post("/suitability", response_model=SuitabilityResponse)
def suitability(body: SuitabilityRequest) -> dict:
    try:
        return score_point(_artifact(), body.latitude, body.longitude)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/map")
def suitability_map() -> FileResponse:
    artifact = _artifact()
    path = artifact.suitability_path
    if not path.is_file():
        raise HTTPException(status_code=503, detail="Suitability GeoTIFF is not ready.")
    return FileResponse(
        path,
        media_type="image/tiff",
        filename="suitability.tif",
    )


@app.get("/cells", response_model=CellsResponse)
def cells() -> dict:
    artifact = _artifact()
    if not artifact.settings.database_url:
        raise HTTPException(status_code=503, detail="DATABASE_URL is not set.")
    from services.data.db import fetch_cell_counts

    try:
        counts = fetch_cell_counts(artifact.settings.database_url)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not query occurrences.") from exc
    return {"cell_size_degrees": 1, "cells": counts}
