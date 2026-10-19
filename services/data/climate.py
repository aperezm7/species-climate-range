"""WorldClim 2.1 bioclimatic rasters at 10 arc-minutes."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import httpx

WORLDCLIM_URL = "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip"
USER_AGENT = "species-climate-range/0.1 (educational; presence-background model)"


def select_bioclim_members(names: list[str]) -> dict[int, str]:
    """Find BIO1 and BIO12 inside the WorldClim zip without matching BIO10 or BIO11."""
    selected: dict[int, str] = {}
    for variable in (1, 12):
        suffix = f"bio_{variable}.tif"
        matches = [name for name in names if name.endswith(suffix) and not name.endswith("/")]
        if len(matches) != 1:
            raise RuntimeError(f"expected one {suffix} in the WorldClim archive, found {matches}")
        selected[variable] = matches[0]
    return selected


def extract_bioclim(zip_path: Path, dest_dir: Path) -> tuple[Path, Path]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        members = select_bioclim_members(archive.namelist())
        outputs: dict[int, Path] = {}
        for variable, member in members.items():
            dest = dest_dir / f"wc2.1_10m_bio_{variable}.tif"
            with archive.open(member) as source, dest.open("wb") as target:
                shutil.copyfileobj(source, target)
            outputs[variable] = dest
    return outputs[1], outputs[12]


def download_worldclim(cache_dir: Path, client: httpx.Client | None = None) -> tuple[Path, Path]:
    """Cache wc2.1 10 arc-minute BIO1 and BIO12. The zip is removed after extract."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    bio1 = cache_dir / "wc2.1_10m_bio_1.tif"
    bio12 = cache_dir / "wc2.1_10m_bio_12.tif"
    if bio1.exists() and bio12.exists():
        return bio1, bio12
    owns_client = client is None
    client = client or httpx.Client(
        timeout=300,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    )
    zip_path = cache_dir / "wc2.1_10m_bio.zip"
    try:
        with client.stream("GET", WORLDCLIM_URL) as response:
            response.raise_for_status()
            with zip_path.open("wb") as handle:
                for chunk in response.iter_bytes():
                    handle.write(chunk)
        extracted = extract_bioclim(zip_path, cache_dir)
    finally:
        if owns_client:
            client.close()
        if zip_path.exists():
            zip_path.unlink()
    return extracted
