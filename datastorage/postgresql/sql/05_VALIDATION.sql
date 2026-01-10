select COUNT(*) from sa.apartments;

select COUNT(*) from dw.dim_districts;

select COUNT(*) from dw.dim_dates;

select COUNT(*) from dw.dim_apartments;

SELECT COUNT(*) FROM dw.fct_apartments;

SELECT * FROM dw.fct_apartments limit 10;

SELECT
    da.description, da.street_address, dd.district_name, ds.source_name
FROM dw.fct_apartments fa
INNER JOIN dw.dim_cities dc ON fa.city_surr_id = dc.city_surr_id
INNER JOIN dw.dim_districts dd ON fa.district_surr_id = dd.district_surr_id
INNER JOIN dw.dim_apartments da ON fa.apartment_surr_id = da.apartment_surr_id
INNER JOIN dw.dim_sources ds ON fa.source_surr_id = ds.source_surr_id
WHERE dc.city_name = 'ქუთაისი' and da.street_address LIKE '%%';
