"""Write the committed synthetic occurrences and climate grid.

The grid is not a WorldClim extract. Presence cells get a warm, wet climate
and every other land cell gets a cool, dry climate, so the offline model has
a separable signal. Longitude -50 is left empty and stands in for ocean.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"

PRESENCES = [
    (-69, -14),
    (-68, -14),
    (-67, -13),
    (-66, -13),
    (-68, -12),
    (-67, -11),
    (-54, -14),
    (-53, -14),
    (-52, -13),
    (-51, -13),
    (-53, -12),
    (-52, -11),
    (-69, 1),
    (-68, 1),
    (-67, 2),
    (-66, 2),
    (-68, 3),
    (-67, 4),
    (-54, 1),
    (-53, 1),
    (-52, 2),
    (-51, 2),
    (-53, 3),
    (-52, 4),
]


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    presence_set = set(PRESENCES)
    with (FIXTURES / "climate_grid.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["longitude", "latitude", "bio1", "bio12"])
        for latitude in range(-15, 6):
            for longitude in range(-70, -49):
                if longitude == -50:
                    writer.writerow([longitude, latitude, "", ""])
                elif (longitude, latitude) in presence_set:
                    writer.writerow([longitude, latitude, 26.0, 2800])
                else:
                    writer.writerow([longitude, latitude, 17.0, 600])
    with (FIXTURES / "occurrences.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "gbif_key",
                "scientific_name",
                "decimalLatitude",
                "decimalLongitude",
                "event_date",
                "basisOfRecord",
                "occurrenceStatus",
            ]
        )
        for index, (longitude, latitude) in enumerate(PRESENCES, start=1):
            writer.writerow(
                [
                    9100000 + index,
                    "Panthera onca",
                    latitude,
                    longitude,
                    "2020-06-15",
                    "HUMAN_OBSERVATION",
                    "PRESENT",
                ]
            )
        writer.writerow([9100101, "Panthera onca", "", -60, "2020-01-01", "HUMAN_OBSERVATION", "PRESENT"])
        writer.writerow([9100102, "Panthera onca", 0, 0, "2020-01-01", "HUMAN_OBSERVATION", "PRESENT"])
        writer.writerow([9100103, "Panthera onca", 95, -60, "2020-01-01", "HUMAN_OBSERVATION", "PRESENT"])
        writer.writerow([9100104, "Panthera onca", -8, -63, "1990-01-01", "FOSSIL_SPECIMEN", "PRESENT"])
        writer.writerow([9100105, "Panthera onca", -8, -62, "2020-01-01", "HUMAN_OBSERVATION", "ABSENT"])
    (FIXTURES / "expected_points.json").write_text(
        json.dumps(
            {
                "high": {"latitude": -14.0, "longitude": -68.0},
                "low": {"latitude": -8.0, "longitude": -63.0},
                "n_presence": len(PRESENCES),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(PRESENCES)} presences and the climate grid to {FIXTURES}")


if __name__ == "__main__":
    main()
