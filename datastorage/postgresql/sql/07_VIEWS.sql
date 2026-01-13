CREATE OR REPLACE VIEW dw.all_apartments_view AS
SELECT
    NULLIF(da.url, 'n.a')                    AS url,
    NULLIF(dc.city_name, 'n.a')              AS city,

    NULLIF(fa.price, -1)                     AS price,
    NULLIF(fa.price_per_sqm, -1)             AS price_per_sqm,
    NULLIF(fa.area_m2, -1)                   AS area_m2,
    NULLIF(fa.bedrooms, -1)                  AS bedrooms,
    NULLIF(fa.floor, -1)                     AS floor,

    NULLIF(da.description, 'n.a')            AS description,
    NULLIF(dd.district_name, 'n.a')          AS district_name,
    NULLIF(da.street_address, 'n.a')         AS street_address,

    NULLIF(ddt.date_dt, '1900-01-01 00:00:00') AS upload_date,

    NULLIF(dtt.transaction_type, 'n.a')      AS transaction_type,
    NULLIF(ds.source_name, 'n.a')             AS source

FROM dw.fct_apartments fa
JOIN dw.dim_cities dc
    ON fa.city_surr_id = dc.city_surr_id
JOIN dw.dim_apartments da
    ON fa.apartment_surr_id = da.apartment_surr_id
JOIN dw.dim_districts dd
    ON fa.district_surr_id = dd.district_surr_id
JOIN dw.dim_dates ddt
    ON fa.date_surr_id = ddt.date_surr_id
JOIN dw.dim_transaction_types dtt
    ON fa.transaction_type_surr_id = dtt.transaction_type_surr_id
JOIN dw.dim_sources ds
    ON fa.source_surr_id = ds.source_surr_id;
