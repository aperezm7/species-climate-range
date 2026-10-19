import json
from pathlib import Path

from fastapi.testclient import TestClient
from rasterio.io import MemoryFile

from services.gateway.app import app

ROOT = Path(__file__).resolve().parents[1]
POINTS = json.loads((ROOT / "tests" / "fixtures" / "expected_points.json").read_text(encoding="utf-8"))


def test_suitability_map_and_missing_database(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_MODE", "fixture")
    monkeypatch.setenv("ARTIFACT_DIR", str(tmp_path))
    monkeypatch.setenv("DATABASE_URL", "")
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        body = health.json()
        assert body["model_ready"] is True
        assert body["scientific_name"] == "Panthera onca"
        assert body["cv_mode"] == "spatial_block"

        high = client.post("/suitability", json=POINTS["high"])
        low = client.post("/suitability", json=POINTS["low"])
        assert high.status_code == 200
        assert low.status_code == 200
        high_body = high.json()
        low_body = low.json()
        assert 0.0 <= low_body["suitability"] < high_body["suitability"] <= 1.0
        assert high_body["suitability"] > 0.7
        assert low_body["suitability"] < 0.3
        assert high_body["bio1_celsius"] == 26.0
        assert low_body["bio12_mm"] == 600.0

        missing = client.post("/suitability", json={"latitude": 0, "longitude": 0})
        assert missing.status_code == 404

        rejected = client.post("/suitability", json={"latitude": 120, "longitude": 10})
        assert rejected.status_code == 422

        cells = client.get("/cells")
        assert cells.status_code == 503

        raster = client.get("/map")
        assert raster.status_code == 200
        assert raster.headers["content-type"].startswith("image/tiff")
        with MemoryFile(raster.content) as mem:
            with mem.open() as dataset:
                assert dataset.count == 1
                assert dataset.crs.to_epsg() == 4326
                assert dataset.width > 1 and dataset.height > 1
                assert dataset.nodata == -9999
