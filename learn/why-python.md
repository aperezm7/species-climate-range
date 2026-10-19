# Why this stays Python

Papers that build a climatic range model often ship R. A close R version of this repo would be:

- `rgbif::occ_search()` for the occurrence search, with `hasCoordinate = TRUE` and geospatial issues excluded
- `geodata::worldclim_global()` or `geodata::worldclim_tile()` for WorldClim 2.1, then `terra` to crop BIO1 and BIO12
- `blockCV::cv_spatial()` for the spatial folds
- `dismo::gbm.step()` or `gbm::gbm()` for the presence-background boosted tree
- `terra::predict()` to write the suitability raster

That stack is how an R lab would do the science. It is not a second runtime in this service. The gateway, the tests, the container, and the model are one Python process: FastAPI, pandas, scikit-learn's `GradientBoostingClassifier`, and rasterio. Adding R would mean another language in the image and a second way for the same functions to drift.

The algorithms that a reader might want to compare with an R script live in `src/` and, with the bodies filled in, in `challenges/hidden/`. `python -m challenges reveal 03` prints one of them.
