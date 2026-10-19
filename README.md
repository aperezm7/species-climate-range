# Species climate range

Where is climatic suitability highest for a focal species?

The default species is jaguar, *Panthera onca*. The name is `scientific_name` in [`config/species.json`](config/species.json). Override it with `SPECIES_SCIENTIFIC_NAME` when `DATA_MODE=live`. Fixture mode keeps using the committed jaguar stand-in and labels the response with whatever name is configured.

Presences come from the GBIF occurrence search (coordinates required, geospatial issues excluded, cap 2000, no download login). Climate is WorldClim 2.1 at 10 arc-minutes, BIO1 and BIO12 only, cropped to the occurrence bounding box. The model is a presence-background gradient boosting tree. Folds are spatial blocks. The score is ROC AUC. The model service writes a suitability GeoTIFF for that box.

The suitability value is a relative score from 0 to 1. It is not a probability of occurrence, and two climate variables are not a range map you should use for a conservation decision.

## Run the API

From this directory:

```bash
docker compose up --build -d
curl -s -X POST http://127.0.0.1:8071/suitability \
  -H 'content-type: application/json' \
  -d '{"latitude": -14.0, "longitude": -68.0}'
```

That request uses the fixture model. The gateway listens on host port **8071**. Postgres is on host port **5433** (`postgresql://sdm:sdm@localhost:5433/occurrences`). The database password is for this local compose file only.

A high cell in the fixture (26°C, 2800 mm) scores higher than a dry cell. Fixture training reports spatial-block ROC AUC 1.0 because those two climates do not overlap. One fitted response is:

```json
{
  "scientific_name": "Panthera onca",
  "common_name": "jaguar",
  "latitude": -14.0,
  "longitude": -68.0,
  "bio1_celsius": 26.0,
  "bio12_mm": 2800.0,
  "suitability": 0.9980788970458557,
  "spatial_block_auc": 1.0,
  "cv_mode": "spatial_block",
  "n_presence": 24,
  "n_background": 160,
  "data_mode": "fixture"
}
```

Other calls:

```bash
curl -s http://127.0.0.1:8071/health
curl -s http://127.0.0.1:8071/cells
curl -s -o suitability.tif http://127.0.0.1:8071/map
docker compose down
```

`GET /map` returns the suitability GeoTIFF (`image/tiff`). `GET /cells` runs the 1-degree count in Postgres. `POST /suitability` returns 404 outside the modeled box or on a cell with no climate, and 422 when latitude or longitude is off the globe.

## Train on the fixture, without the network

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
DATA_MODE=fixture DATABASE_URL= python -m services.model.train
```

`DATA_MODE` defaults to `fixture`, so the variable is optional. The command reads `tests/fixtures/` and writes `data/artifacts/model.joblib`, `metrics.json`, and `suitability.tif`. It does not call GBIF or WorldClim.

Live mode, when you want the real search and the real rasters:

```bash
DATA_MODE=live python -m services.model.train
```

The first live run downloads the WorldClim zip (about 50 MB) and up to 2000 GBIF records. Both are cached under `data/cache/`. Details of what is committed and what is downloaded are in [DATA.md](DATA.md).

## Tests

CI runs this, with Postgres available:

```bash
CHALLENGE_SOLUTIONS=hidden DATA_MODE=fixture \
  DATABASE_URL=postgresql://sdm:sdm@localhost:5433/occurrences \
  REQUIRE_POSTGRES=1 pytest
```

Without Postgres the database test is skipped, and this still runs the hidden solutions and the fixture service tests:

```bash
CHALLENGE_SOLUTIONS=hidden pytest
```

`CHALLENGE_SOLUTIONS=hidden` is what makes the five challenge tests import `challenges/hidden/` instead of the starters. The starters raise `NotImplementedError` until you fill them in. To work one challenge:

```bash
pytest challenges/01_validate_gbif_point
python -m challenges reveal 01
```

## Challenges

| # | Directory | Task |
| --- | --- | --- |
| 01 | `challenges/01_validate_gbif_point` | Drop null coordinates and (0, 0) |
| 02 | `challenges/02_spatial_thinning` | Keep one record per grid cell |
| 03 | `challenges/03_sample_background` | Draw background points inside a bounding box |
| 04 | `challenges/04_roc_auc` | ROC AUC from scores and labels |
| 05 | `challenges/05_cell_count_sql` | SQL count of records per 1-degree cell |

```bash
python -m challenges reveal 03
```

prints the solution and a short explanation. `learn/sql.md` annotates the cell-count query. `learn/climate.md` explains why further BIOCLIM variables wait on a collinearity check. `learn/why-python.md` says what the R stack would have been.

## Layout

```text
services/gateway     FastAPI. The only public entrypoint.
services/data        GBIF search, WorldClim cache, fixture grids, Postgres
services/features    thinning, background, design matrix
services/model       train and score
src/                 functions the services import
challenges/          starters, tests, and hidden solutions
```

Postgres stores the validated occurrence table. Microbiology-style wide matrices are not used here; the cell count is a grouped query, which is why it is SQL.

## Citations

- GBIF.org occurrence search API. https://api.gbif.org/v1/occurrence/search and https://www.gbif.org
- Fick, S.E. and Hijmans, R.J. (2017) WorldClim 2: new 1-km spatial resolution climate surfaces for global land areas. International Journal of Climatology 37: 4302–4315. https://doi.org/10.1002/joc.5086
- Roberts, D.R. et al. (2017) Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography 40: 913–929. https://doi.org/10.1111/ecog.02881
- Dormann, C.F. et al. (2013) Collinearity: a review of methods to deal with it and a simulation study evaluating their performance. Ecography 36: 27–46. https://doi.org/10.1111/j.1600-0587.2012.07348.x

## Limits

The GBIF search is capped and ordered by GBIF, so the presences are not a spatial sample of the species. Background points are uniform in degree space inside the presence box, not a target-group background. Spatial blocks are a 2 by 2 split of that box. If a fold does not contain both classes, it is skipped; if fewer than two folds remain, metrics record `cv_mode: random_fallback`. Suitability is climatic only, at 10 arc-minutes in live mode and 1 degree in the fixture.
