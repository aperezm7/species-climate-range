"""GBIF occurrence search. No download login."""

from __future__ import annotations

import httpx

GBIF_SEARCH_URL = "https://api.gbif.org/v1/occurrence/search"
PAGE_SIZE = 300
USER_AGENT = "species-climate-range/0.1 (educational; presence-background model)"
EXCLUDED_BASIS = {"FOSSIL_SPECIMEN", "LIVING_SPECIMEN"}


def include_record(raw: dict) -> bool:
    """Drop fossils, captive animals, and explicit absences."""
    basis = raw.get("basisOfRecord") or raw.get("basis_of_record")
    if basis in EXCLUDED_BASIS:
        return False
    status = raw.get("occurrenceStatus") or raw.get("occurrence_status")
    if status == "ABSENT":
        return False
    return True


def fetch_gbif(
    scientific_name: str,
    limit: int,
    client: httpx.Client | None = None,
) -> list[dict]:
    """Page the public search API until `limit` candidate records are kept.

    Parameters are the search contract: coordinates required, geospatial issues
    excluded. The search order is GBIF's default, not a random sample.
    """
    owns_client = client is None
    client = client or httpx.Client(
        timeout=60,
        headers={"User-Agent": USER_AGENT},
        follow_redirects=True,
    )
    kept: list[dict] = []
    offset = 0
    try:
        while len(kept) < limit and offset <= 10000:
            response = client.get(
                GBIF_SEARCH_URL,
                params={
                    "scientificName": scientific_name,
                    "hasCoordinate": "true",
                    "hasGeospatialIssue": "false",
                    "limit": PAGE_SIZE,
                    "offset": offset,
                },
            )
            response.raise_for_status()
            payload = response.json()
            results = payload.get("results", [])
            for raw in results:
                if not include_record(raw):
                    continue
                kept.append(raw)
                if len(kept) >= limit:
                    break
            if payload.get("endOfRecords", True) or not results:
                break
            offset += PAGE_SIZE
        return kept
    finally:
        if owns_client:
            client.close()
