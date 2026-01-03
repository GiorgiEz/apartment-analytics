import pandas as pd
from scrape_clean_analyze.data_cleaning.DataCleaning import DataCleaning

def test_normalize_bedrooms():
    df = pd.DataFrame({
        'bedrooms': ['საძ. 1', '2', None, 'unknown', pd.NA],
        'area_m2': [40, 80, 120, 60, 120]
    })

    cleaner = DataCleaning(df)
    cleaner._normalize_bedrooms()

    expected = pd.Series(
        [1, 2, 3, 2, 3],
        name='bedrooms',
        dtype='Int64'
    )

    pd.testing.assert_series_equal(
        cleaner.apartments_df['bedrooms'],
        expected
    )
