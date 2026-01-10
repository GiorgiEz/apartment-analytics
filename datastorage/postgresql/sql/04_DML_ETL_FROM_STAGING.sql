-- =====================================
-- 04_DML_ETL_INIT_DIMENSIONS.sql
-- =====================================

-- INSERT FROM STAGING TABLE TO DIMENSION TABLES

-- LOAD DIM_APARTMENTS
BEGIN;

INSERT INTO dw.dim_apartments (
    street_address,
    description,
    url
)
SELECT DISTINCT
    COALESCE(NULLIF(street_address, ''), 'n.a') AS street_address,
    COALESCE(NULLIF(description, ''), 'n.a') AS description,
    url
FROM sa.apartments
WHERE url IS NOT NULL
ON CONFLICT (url) DO NOTHING
RETURNING *;

COMMIT;

-- LOAD DIM_DISTRICTS
BEGIN;

INSERT INTO dw.dim_districts (
    city_surr_id,
    district_name
)
SELECT DISTINCT
    COALESCE(dc.city_surr_id, -1) AS city_surr_id,
    COALESCE(NULLIF(sa.district_name, ''), 'n.a') AS district_name
FROM sa.apartments sa
LEFT JOIN dw.dim_cities dc
    ON sa.city = dc.city_name
ON CONFLICT (city_surr_id, district_name) DO NOTHING
RETURNING *;

COMMIT;

-- LOAD DIM_DATES
BEGIN;

INSERT INTO dw.dim_dates (
    date_dt,
    date_year,
    date_month,
    date_day,
    date_hour,
    date_minute,
    date_day_of_week
)
SELECT DISTINCT
    dt AS date_dt,
    EXTRACT(YEAR FROM dt)::int,
    EXTRACT(MONTH FROM dt)::int,
    EXTRACT(DAY FROM dt)::int,
    EXTRACT(HOUR FROM dt)::int,
    EXTRACT(MINUTE FROM dt)::int,
    EXTRACT(ISODOW FROM dt)::smallint
FROM (
    SELECT upload_date::timestamp AS dt
    FROM sa.apartments
    WHERE upload_date IS NOT NULL
) s
ON CONFLICT (date_dt) DO NOTHING
RETURNING *;

COMMIT;

-- INSERT FROM STAGING TABLE TO FACT TABLE

-- LOAD FCT_APARTMENTS
BEGIN;

INSERT INTO dw.fct_apartments (
    date_surr_id,
    city_surr_id,
    district_surr_id,
    transaction_type_surr_id,
    source_surr_id,
    apartment_surr_id,
    price,
    price_per_sqm,
    area_m2,
    bedrooms,
    floor
)
SELECT
    COALESCE(ddt.date_surr_id, -1)                 AS date_surr_id,
    COALESCE(dc.city_surr_id, -1)                  AS city_surr_id,
    COALESCE(dd.district_surr_id, -1)              AS district_surr_id,
    COALESCE(dtt.transaction_type_surr_id, -1)    AS transaction_type_surr_id,
    COALESCE(ds.source_surr_id, -1)                AS source_surr_id,
    COALESCE(da.apartment_surr_id, -1)             AS apartment_surr_id,

    sa.price::DECIMAL(12,2)         AS price,
    sa.price_per_sqm::DECIMAL(10,2) AS price_per_sqm,
    sa.area_m2::DECIMAL(8,2)        AS area_m2,
    COALESCE(FLOOR(sa.bedrooms::NUMERIC)::INT, -1) AS bedrooms,
    COALESCE(FLOOR(sa.floor::NUMERIC)::INT, -1)    AS floor

FROM sa.apartments sa
-- Apartment
LEFT JOIN dw.dim_apartments da
    ON sa.url = da.url
-- City
LEFT JOIN dw.dim_cities dc
    ON sa.city = dc.city_name
-- District (city-dependent)
LEFT JOIN dw.dim_districts dd
    ON dd.city_surr_id = COALESCE(dc.city_surr_id, -1)
   AND dd.district_name = COALESCE(NULLIF(sa.district_name, ''), 'n.a')
-- Transaction type
LEFT JOIN dw.dim_transaction_types dtt
    ON sa.transaction_type = dtt.transaction_type
-- Source
LEFT JOIN dw.dim_sources ds
    ON sa.source = ds.source_name
-- Date
LEFT JOIN dw.dim_dates ddt
    ON sa.upload_date::timestamp = ddt.date_dt

WHERE
    sa.price IS NOT NULL
    AND sa.price_per_sqm IS NOT NULL
    AND sa.area_m2 IS NOT NULL
ON CONFLICT DO NOTHING;

COMMIT;

-- CLEAN STAGING AFTER SUCCESSFUL LOAD
BEGIN;
TRUNCATE TABLE sa.apartments;
COMMIT;