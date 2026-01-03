import pandas as pd
from scrape_clean_analyze.data_cleaning.DataCleaning import DataCleaning


def test_normalize_area_m2():
    df = pd.DataFrame({
        'area_m2': [
            '50 მ²',
            '45 მ2',
            '60',
            '  75 მ² ',
            'unknown',
            None
        ]
    })

    cleaner = DataCleaning(df)
    cleaner._normalize_area_m2()

    result = cleaner.apartments_df['area_m2']

    expected = pd.Series(
        [50.0, 45.0, 60.0, 75.0, pd.NA, pd.NA],
        name="area_m2",
        dtype="Float64"
    )

    pd.testing.assert_series_equal(result, expected)
