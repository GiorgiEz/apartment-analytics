-- =====================================
-- 03_DML_INIT_DIMENSIONS.sql
-- =====================================

/* 1. INSERT DEFAULT ROWS IN DIMENSION TABLES */
BEGIN;

-- DIM_SOURCES
INSERT INTO dw.dim_sources (
    source_surr_id,
    source_name
)
VALUES (-1,'n.a')
ON CONFLICT DO NOTHING
RETURNING *;

-- DIM_TRANSACTION_TYPES
INSERT INTO dw.dim_transaction_types (
    transaction_type_surr_id,
    transaction_type
)
VALUES (-1,'n.a')
ON CONFLICT DO NOTHING
RETURNING *;

-- DIM_CITIES
INSERT INTO dw.dim_cities (
    city_surr_id,
    city_name
)
VALUES (-1,'n.a')
ON CONFLICT DO NOTHING
RETURNING *;

-- DIM_DISTRICTS
INSERT INTO dw.dim_districts (
    district_surr_id,
    city_surr_id,
    district_name
)
VALUES (-1,-1,'n.a')
ON CONFLICT DO NOTHING
RETURNING *;

-- DIM_DATES
INSERT INTO dw.dim_dates (
    date_surr_id,
    date_dt,
    date_year,
    date_month,
    date_day,
    date_hour,
    date_minute,
    date_day_of_week
)
VALUES (-1,'1900-01-01 00:00:00',
    1900,1,1,0,0,1
)
ON CONFLICT DO NOTHING
RETURNING *;

-- DIM_APARTMENTS
INSERT INTO dw.dim_apartments (
    apartment_surr_id,
    street_address,
    description,
    url
)
VALUES (-1,'n.a','n.a','n.a')
ON CONFLICT DO NOTHING
RETURNING *;

COMMIT;


/* INSERT FIXED REFERENCE DIMENSIONS */

BEGIN;
-- DIM_SOURCES
INSERT INTO dw.dim_sources (source_name)
VALUES
    ('myhome.ge'),
    ('livo.ge'),
    ('home.ss.ge')
ON CONFLICT DO NOTHING
RETURNING *;

-- DIM_TRANSACTION_TYPES
INSERT INTO dw.dim_transaction_types (transaction_type)
VALUES
    ('იყიდება'),
    ('ქირავდება თვიურად'),
    ('ქირავდება დღიურად'),
    ('გირავდება')
ON CONFLICT DO NOTHING
RETURNING *;

-- DIM_CITIES
INSERT INTO dw.dim_cities (city_name)
VALUES
    ('თბილისი'),
    ('ბათუმი'),
    ('ქუთაისი')
ON CONFLICT DO NOTHING
RETURNING *;

COMMIT;