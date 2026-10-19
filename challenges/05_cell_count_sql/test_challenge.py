import math
import sqlite3

from challenges.loader import load_challenge


def _counts(rows):
    sql = load_challenge("05_cell_count_sql").cell_count_sql()
    connection = sqlite3.connect(":memory:")
    connection.create_function("floor", 1, math.floor)
    connection.execute(
        "CREATE TABLE occurrences (latitude REAL, longitude REAL, scientific_name TEXT)"
    )
    connection.executemany("INSERT INTO occurrences (latitude, longitude) VALUES (?, ?)", rows)
    cursor = connection.execute(sql)
    assert [column[0] for column in cursor.description] == ["lat_cell", "lon_cell", "n_records"]
    fetched = cursor.fetchall()
    return sorted((int(lat), int(lon), int(count)) for lat, lon, count in fetched)


def test_negative_coordinates_use_floor_toward_negative_infinity():
    rows = [(-3.2, -60.2), (-3.8, -60.9), (-3.1, -61.0), (0.2, -59.1)]
    assert _counts(rows) == [(-4, -61, 3), (0, -60, 1)]


def test_positive_cell_and_empty_table():
    assert _counts([(10.2, 20.2), (10.9, 20.8)]) == [(10, 20, 2)]
    assert _counts([]) == []
