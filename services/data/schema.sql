CREATE TABLE IF NOT EXISTS occurrences (
    gbif_key BIGINT PRIMARY KEY,
    scientific_name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    event_date TEXT
);
