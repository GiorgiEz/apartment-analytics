CREATE OR REPLACE VIEW dw.all_apartments AS
SELECT
    da.url as url,
    dc.city_name as city,
    fa.price as price,
    fa.price_per_sqm as price_per_sqm,
    da.description as description,
    dd.district_name as district_name,
    da.street_address as street_address,
    fa.area_m2 as area_m2,
    fa.bedrooms as bedrooms,
    fa.floor as floor,
    ddt.date_dt as upload_date,
    dtt.transaction_type as transaction_type,
    ds.source_name as source
FROM dw.fct_apartments fa
INNER JOIN dw.dim_cities dc on fa.city_surr_id = dc.city_surr_id
INNER JOIN dw.dim_apartments da ON fa.apartment_surr_id = da.apartment_surr_id
INNER JOIN dw.dim_districts dd ON fa.district_surr_id = dd.district_surr_id
INNER JOIN dw.dim_dates ddt ON fa.date_surr_id = ddt.date_surr_id
INNER JOIN dw.dim_transaction_types dtt ON fa.transaction_type_surr_id = dtt.transaction_type_surr_id
INNER JOIN dw.dim_sources ds ON fa.source_surr_id = ds.source_surr_id
;
