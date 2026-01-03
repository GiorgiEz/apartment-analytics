import pandas as pd
from scrape_clean_analyze.data_cleaning.DataCleaning import DataCleaning

def test_normalize_price_per_sqm():
    df = pd.DataFrame({
        'price_per_sqm': [
            '500.0',
            '2,059 $ /მ2',
            '4,196 / მ²',
            None,
            'negotiable',
        ],
        'price': [None, None, None, 100000, 100000],
        'area_m2': [None, None, None, 50, 50],
    })

    currency_rate = 0.37
    cleaner = DataCleaning(df, currency_rate=currency_rate)
    cleaner._normalize_price_per_sqm()

    expected = pd.Series(
        [
            500.0 * currency_rate,
            2059.0,
            4196 * currency_rate,
            2000.0,
            2000.0,
        ],
        name='price_per_sqm',
        dtype='Float64'
    )

    pd.testing.assert_series_equal(
        cleaner.apartments_df['price_per_sqm'],
        expected
    )
