import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

from services.data.climate import extract_bioclim, select_bioclim_members
from src.grid import crop_pair, locate, scale_band, temperature_scale


def test_member_names_do_not_confuse_bio1_with_bio10():
    names = [
        "wc2.1_10m_bio_1.tif",
        "wc2.1_10m_bio_10.tif",
        "wc2.1_10m_bio_11.tif",
        "wc2.1_10m_bio_12.tif",
        "wc2.1_10m_bio_19.tif",
    ]
    selected = select_bioclim_members(names)
    assert selected[1].endswith("bio_1.tif")
    assert selected[12].endswith("bio_12.tif")


def test_extract_writes_only_bio1_and_bio12(tmp_path: Path):
    zip_path = tmp_path / "worldclim.zip"
    with zipfile.ZipFile(zip_path, "w") as archive:
        archive.writestr("wc2.1_10m_bio_1.tif", b"bio1")
        archive.writestr("wc2.1_10m_bio_10.tif", b"bio10")
        archive.writestr("wc2.1_10m_bio_12.tif", b"bio12")
    bio1, bio12 = extract_bioclim(zip_path, tmp_path / "out")
    assert bio1.read_bytes() == b"bio1"
    assert bio12.read_bytes() == b"bio12"
    assert not (tmp_path / "out" / "wc2.1_10m_bio_10.tif").exists()


def test_integer_worldclim_temperature_is_stored_as_celsius_times_ten():
    raw = np.array([[265, -150], [-32768, 0]], dtype="int16")
    assert temperature_scale(raw, nodata=-32768) == 0.1
    scaled = scale_band(raw, nodata=-32768, worldclim=True, scale=0.1)
    assert scaled[0, 0] == np.float32(26.5)
    assert scaled[0, 1] == np.float32(-15.0)
    assert scaled[1, 0] == np.float32(-9999.0)
    assert scaled[1, 1] == np.float32(0.0)


def test_float_worldclim_temperature_is_already_celsius():
    raw = np.array([[27.5, -54.7], [-3.4e38, 0.0]], dtype="float32")
    assert temperature_scale(raw, nodata=-3.4e38) == 1.0


def test_crop_keeps_a_known_cell(tmp_path: Path):
    transform = from_origin(-2, 2, 1, 1)
    values = np.arange(16, dtype="float32").reshape(4, 4)
    path = tmp_path / "band.tif"
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=4,
        width=4,
        count=1,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        nodata=-9999,
    ) as dataset:
        dataset.write(values, 1)
    grid = crop_pair(path, path, (-1.2, -1.2, 0.2, 0.2), tmp_path / "crop", worldclim=False)
    status, sampled = locate(grid, -0.5, -0.5)
    assert status == "ok"
    assert sampled is not None
    assert sampled[0] == sampled[1]
