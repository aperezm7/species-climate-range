import json

from services.model import train as train_module
from services.model.train import train
from src.settings import load_settings


def test_fixture_train_stays_offline_and_separates_the_niche(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_MODE", "fixture")
    monkeypatch.setenv("ARTIFACT_DIR", str(tmp_path))
    monkeypatch.setenv("DATABASE_URL", "")

    def _forbidden(*_args, **_kwargs):
        raise AssertionError("fixture training must not download GBIF or WorldClim")

    monkeypatch.setattr(train_module, "download_worldclim", _forbidden)

    artifact = train(load_settings())
    metrics = artifact.metrics
    assert metrics["data_mode"] == "fixture"
    assert metrics["scientific_name"] == "Panthera onca"
    assert metrics["n_presence"] == 24
    assert metrics["n_raw"] > metrics["n_occurrence_rows"] == 24
    assert metrics["n_background"] >= 24
    assert metrics["cv_mode"] == "spatial_block"
    assert metrics["spatial_block_auc"] > 0.9
    assert artifact.suitability_path.is_file()
    saved = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert saved["n_presence"] == 24
