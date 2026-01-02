import pandas as pd
from scrape_clean_analyze.data_cleaning.DataCleaning import DataCleaning

def test_clean_and_transform_price():
    df = pd.DataFrame({
        'price': [
            '100,000 $',
            '105,000$',
            '103,808',
            '103,808 ₾',
            None,
            'negotiable',
        ]
    })

    cleaner = DataCleaning(df, currency_rate=0.37)
    cleaner._clean_and_transform_price()

    result = cleaner.apartments_df['price']

    expected = pd.Series(
        [
            100000.0,
            105000.0,
            103808 * 0.37,
            103808 * 0.37,
            pd.NA,
            pd.NA,
        ],
        name='price',
        dtype='Float64'
    )

    pd.testing.assert_series_equal(result, expected)
