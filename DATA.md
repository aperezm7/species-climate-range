# Data

The question is where climatic suitability is highest for a focal species. The default species is jaguar, *Panthera onca*, set in `config/species.json`.

There are two data paths. They do not share grids, and a score from one is not a score from the other.

| | Fixture (`DATA_MODE=fixture`, the default) | Live (`DATA_MODE=live`) |
| --- | --- | --- |
| Occurrences | `tests/fixtures/occurrences.csv`, synthetic | GBIF occurrence search, cap 2000 |
| Climate | `tests/fixtures/climate_grid.csv`, synthetic 1° grid | WorldClim 2.1 at 10 arc-minutes, BIO1 and BIO12, cropped to the occurrence box |
| What the fit can show | The pipeline separates a painted niche. Spatial-block AUC near 1.0 is that separation, not a jaguar result | Climatic suitability for the configured species |
| Committed? | Yes, the CSVs | No. Cache and rasters stay in `data/` |

Docker Compose and CI use the fixture path so they do not download GBIF or WorldClim.

## Live path

`DATA_MODE=live` downloads the files below. Nothing in this section is committed.

### GBIF occurrence search

- URL: `https://api.gbif.org/v1/occurrence/search`
- Parameters: `scientificName` from config, `hasCoordinate=true`, `hasGeospatialIssue=false`, pages of 300, stop at `gbif_limit` (default 2000)
- No GBIF download login. This is the public search API, so there is no download DOI. Cite GBIF as the source: GBIF.org (https://www.gbif.org).
- The search returns records in GBIF's default order. It is not a random or spatially balanced sample. The cap is the first 2000 records that pass the filters below, not a designed subsample of the full species.
- Dropped after download: `FOSSIL_SPECIMEN`, `LIVING_SPECIMEN`, and `occurrenceStatus=ABSENT`. Coordinate checks then drop nulls, `(0, 0)`, and values outside WGS84.
- Cache: `data/cache/gbif/<species>.json`. Set `REFRESH_DATA=1` to ignore it.

### WorldClim 2.1, 10 arc-minutes

- Archive: `https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_bio.zip` (about 50 MB)
- The `10m` in the filename is 10 arc-minutes, not 10 metres.
- Citation: Fick, S.E. and Hijmans, R.J. (2017) WorldClim 2: new 1-km spatial resolution climate surfaces for global land areas. International Journal of Climatology 37: 4302–4315. https://doi.org/10.1002/joc.5086
- Only BIO1 and BIO12 are extracted. BIO12 is millimetres. In this float archive BIO1 is already °C (annual means fall around −55 to 31). Integer WorldClim stacks store temperature as °C × 10; the loader divides BIO1 by 10 only when absolute values in the crop exceed 80. Ocean and the source nodata value are stored as `-9999` after cropping.
- The rasters are cropped to the occurrence bounding box plus `BBOX_BUFFER_DEG` (default 1°).
- Cache: `data/cache/worldclim/wc2.1_10m_bio_1.tif` and `wc2.1_10m_bio_12.tif`. The zip is deleted after extract.
- Why those two variables, and why the other 17 wait: `learn/climate.md`.

## Fixture path

These files are the default train. They are synthetic. They are not a GBIF extract and not a WorldClim crop. Do not read a fixture AUC, or a curl against a fixture server, as the live jaguar model.

| File | What it is |
| --- | --- |
| `tests/fixtures/occurrences.csv` | 24 jaguar-shaped presences, plus rows the loader must drop: a null coordinate, `(0, 0)`, a latitude of 95, a fossil, and an absence |
| `tests/fixtures/climate_grid.csv` | 1° grid from 70°W–50°W and 15°S–5°N. Presence cells are 26°C and 2800 mm. Other land cells are 17°C and 600 mm. Longitude 50°W is empty, as ocean |
| `tests/fixtures/expected_points.json` | One high cell and one low cell for the API check |

The service builds GeoTIFFs from `climate_grid.csv` at train time. Those GeoTIFFs, the fitted model, and `suitability.tif` are written under `data/artifacts/` and are not committed.

Regenerate the CSVs with `python scripts/build_fixtures.py`.
