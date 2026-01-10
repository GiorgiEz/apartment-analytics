-- 02_STAGING.sql

-- STAGING SCHEMA
CREATE SCHEMA IF NOT EXISTS sa;

-- STAGING TABLE (RAW, PERMISSIVE)
DROP TABLE IF EXISTS sa.apartments;

CREATE TABLE sa.apartments (
    url               TEXT,
    city              TEXT,
    price             TEXT,
    price_per_sqm     TEXT,
    description       TEXT,
    district_name     TEXT,
    street_address    TEXT,
    area_m2           TEXT,
    bedrooms          TEXT,
    floor             TEXT,
    upload_date       TEXT,
    transaction_type  TEXT,
    source            TEXT
);

-- =====================================
-- Import CSV to sa.apartments table
-- =====================================
