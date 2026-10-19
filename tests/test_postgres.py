import os

import psycopg
import pytest

from services.data.db import SCHEMA_PATH
from src.sql import cell_count_sql


def test_cell_count_query_on_postgres():
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        if os.environ.get("REQUIRE_POSTGRES") == "1":
            pytest.fail("DATABASE_URL is required")
        pytest.skip("DATABASE_URL is not set")
    rows = [(-3.2, -60.2), (-3.8, -60.9), (-3.1, -61.0), (0.2, -59.1)]
    connection = psycopg.connect(database_url)
    try:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
            cursor.execute("TRUNCATE occurrences")
            cursor.executemany(
                """
                INSERT INTO occurrences (gbif_key, scientific_name, latitude, longitude)
                VALUES (%s, %s, %s, %s)
                """,
                [
                    (index, "Panthera onca", latitude, longitude)
                    for index, (latitude, longitude) in enumerate(rows, start=1)
                ],
            )
            cursor.execute(cell_count_sql())
            fetched = sorted(
                (int(lat_cell), int(lon_cell), int(n_records))
                for lat_cell, lon_cell, n_records in cursor.fetchall()
            )
        assert fetched == [(-4, -61, 3), (0, -60, 1)]
    finally:
        connection.rollback()
        connection.close()
