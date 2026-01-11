select COUNT(*) from sa.apartments;

select COUNT(*) from dw.dim_districts;

select COUNT(*) from dw.dim_dates;

select COUNT(*) from dw.dim_apartments;

SELECT COUNT(*) FROM dw.fct_apartments;

SELECT COUNT(*) from dw.all_apartments;

SELECT * FROM dw.fct_apartments limit 10;

SELECT da.url, dd.date_dt, fa.price FROM dw.fct_apartments fa
INNER JOIN dw.dim_apartments da ON fa.apartment_surr_id = da.apartment_surr_id
INNER JOIN dw.dim_dates dd on dd.date_surr_id = fa.date_surr_id
where url = 'https://www.myhome.ge/pr/18379269/qiravdeba-1-otaxiani-bina-qutaisshi/';

SELECT url, COUNT(*) FROM dw.fct_apartments fa
INNER JOIN dw.dim_apartments da ON fa.apartment_surr_id = da.apartment_surr_id
INNER JOIN dw.dim_dates dd on dd.date_surr_id = fa.date_surr_id
GROUP BY da.url having COUNT(*) > 1;

SELECT
    da.description, da.street_address, dd.district_name, ds.source_name
FROM dw.fct_apartments fa
INNER JOIN dw.dim_cities dc ON fa.city_surr_id = dc.city_surr_id
INNER JOIN dw.dim_districts dd ON fa.district_surr_id = dd.district_surr_id
INNER JOIN dw.dim_apartments da ON fa.apartment_surr_id = da.apartment_surr_id
INNER JOIN dw.dim_sources ds ON fa.source_surr_id = ds.source_surr_id
WHERE dc.city_name = 'ქუთაისი' and da.street_address LIKE '%%';

SELECT
    dd.district_name, COUNT(*)
FROM dw.fct_apartments fa
INNER JOIN dw.dim_districts dd ON fa.district_surr_id = dd.district_surr_id
GROUP BY dd.district_name;

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
