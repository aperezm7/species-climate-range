import json

import httpx

from services.data.gbif import fetch_gbif
from services.data.occurrences import load_occurrence_rows, prepare_records, species_slug
from src.settings import Settings


def _settings(tmp_path, **overrides) -> Settings:
    values = dict(
        scientific_name="Panthera onca",
        common_name="jaguar",
        gbif_limit=3,
        data_mode="live",
        database_url="",
        artifact_dir=tmp_path / "artifacts",
        cache_dir=tmp_path / "cache",
        fixture_dir=tmp_path / "fixtures",
        root=tmp_path,
        random_seed=42,
        n_lat_blocks=2,
        n_lon_blocks=2,
        background_per_block=40,
        bbox_buffer_deg=1,
    )
    values.update(overrides)
    return Settings(**values)


def test_search_pages_until_the_cap_and_drops_fossils():
    pages = {
        0: {
            "endOfRecords": False,
            "results": [
                {
                    "gbifID": 1,
                    "decimalLatitude": -3.0,
                    "decimalLongitude": -60.0,
                    "basisOfRecord": "FOSSIL_SPECIMEN",
                    "occurrenceStatus": "PRESENT",
                    "species": "Panthera onca",
                },
                {
                    "gbifID": 2,
                    "decimalLatitude": -4.0,
                    "decimalLongitude": -61.0,
                    "basisOfRecord": "HUMAN_OBSERVATION",
                    "occurrenceStatus": "PRESENT",
                    "species": "Panthera onca",
                },
                {
                    "gbifID": 3,
                    "decimalLatitude": -5.0,
                    "decimalLongitude": -62.0,
                    "basisOfRecord": "HUMAN_OBSERVATION",
                    "occurrenceStatus": "ABSENT",
                    "species": "Panthera onca",
                },
            ],
        },
        300: {
            "endOfRecords": True,
            "results": [
                {
                    "gbifID": 4,
                    "decimalLatitude": 0,
                    "decimalLongitude": 0,
                    "basisOfRecord": "HUMAN_OBSERVATION",
                    "occurrenceStatus": "PRESENT",
                    "species": "Panthera onca",
                },
                {
                    "gbifID": 5,
                    "decimalLatitude": -6.0,
                    "decimalLongitude": -63.0,
                    "basisOfRecord": "OBSERVATION",
                    "occurrenceStatus": "PRESENT",
                    "species": "Panthera onca",
                },
                {
                    "gbifID": 6,
                    "decimalLatitude": -7.0,
                    "decimalLongitude": -64.0,
                    "basisOfRecord": "HUMAN_OBSERVATION",
                    "occurrenceStatus": "PRESENT",
                    "species": "Panthera onca",
                },
            ],
        },
    }
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["scientificName"] == "Panthera onca"
        assert request.url.params["hasCoordinate"] == "true"
        assert request.url.params["hasGeospatialIssue"] == "false"
        offset = int(request.url.params["offset"])
        seen.append(offset)
        return httpx.Response(200, json=pages[offset])

    client = httpx.Client(transport=httpx.MockTransport(handler))
    rows = fetch_gbif("Panthera onca", limit=3, client=client)
    # The cap counts search hits after the basis filter. (0, 0) is still a hit;
    # coordinate validation removes it on the next step.
    assert [row["gbifID"] for row in rows] == [2, 4, 5]
    assert seen == [0, 300]
    prepared = prepare_records(rows, "Panthera onca")
    assert [row["gbif_key"] for row in prepared] == [2, 5]


def test_live_loader_uses_the_cache_and_does_not_call_gbif_again(tmp_path):
    settings = _settings(tmp_path)
    cache = settings.cache_dir / "gbif" / f"{species_slug(settings.scientific_name)}.json"
    cache.parent.mkdir(parents=True)
    cache.write_text(
        json.dumps(
            [
                {
                    "gbifID": 9,
                    "decimalLatitude": -2.0,
                    "decimalLongitude": -59.0,
                    "species": "Panthera onca",
                    "basisOfRecord": "HUMAN_OBSERVATION",
                    "occurrenceStatus": "PRESENT",
                }
            ]
        ),
        encoding="utf-8",
    )

    def handler(_request: httpx.Request) -> httpx.Response:
        raise AssertionError("cached occurrences must not hit GBIF")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    rows = load_occurrence_rows(settings, client=client)
    assert rows[0]["gbifID"] == 9
