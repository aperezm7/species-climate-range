"""Runtime configuration. The species name lives in config/species.json."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "species.json"


@dataclass(frozen=True)
class Settings:
    scientific_name: str
    common_name: str
    gbif_limit: int
    data_mode: str
    database_url: str
    artifact_dir: Path
    cache_dir: Path
    fixture_dir: Path
    root: Path
    random_seed: int
    n_lat_blocks: int
    n_lon_blocks: int
    background_per_block: int
    bbox_buffer_deg: float


def load_settings() -> Settings:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    scientific_name = os.environ.get(
        "SPECIES_SCIENTIFIC_NAME", payload["scientific_name"]
    ).strip()
    common_name = os.environ.get("SPECIES_COMMON_NAME", payload["common_name"]).strip()
    gbif_limit = int(os.environ.get("GBIF_LIMIT", payload.get("gbif_limit", 2000)))
    data_mode = os.environ.get("DATA_MODE", "fixture").strip().lower()
    if data_mode not in {"fixture", "live"}:
        raise ValueError("DATA_MODE must be fixture or live")
    if gbif_limit < 1:
        raise ValueError("GBIF_LIMIT must be at least 1")
    return Settings(
        scientific_name=scientific_name,
        common_name=common_name,
        gbif_limit=gbif_limit,
        data_mode=data_mode,
        database_url=os.environ.get("DATABASE_URL", "").strip(),
        artifact_dir=Path(os.environ.get("ARTIFACT_DIR", ROOT / "data" / "artifacts")),
        cache_dir=Path(os.environ.get("CACHE_DIR", ROOT / "data" / "cache")),
        fixture_dir=Path(os.environ.get("FIXTURE_DIR", ROOT / "tests" / "fixtures")),
        root=ROOT,
        random_seed=int(os.environ.get("RANDOM_SEED", "42")),
        n_lat_blocks=int(os.environ.get("N_LAT_BLOCKS", "2")),
        n_lon_blocks=int(os.environ.get("N_LON_BLOCKS", "2")),
        background_per_block=int(os.environ.get("BACKGROUND_PER_BLOCK", "40")),
        bbox_buffer_deg=float(os.environ.get("BBOX_BUFFER_DEG", "1")),
    )
