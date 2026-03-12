import pandas as pd
from data_cleaning.DataCleaning import DataCleaning

def test_normalize_price():
    df = pd.DataFrame({
        'price': [
            '500',
            '100,000 $',
            '105,000$',
            0,
            '103,808 ₾',
            None,
            'negotiable',
        ]
    })

    currency_rate = 0.37
    cleaner = DataCleaning(df, currency_rate=currency_rate)
    cleaner._normalize_price()

    result = cleaner.apartments_df['price']

    expected = pd.Series(
        [
            500.0,
            100000.0,
            105000.0,
            pd.NA,
            103808 * currency_rate,
            pd.NA,
            pd.NA,
        ],
        name='price',
        dtype='Float64'
    )

    pd.testing.assert_series_equal(result, expected)
