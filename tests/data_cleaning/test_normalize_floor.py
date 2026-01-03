import pandas as pd
from scrape_clean_analyze.data_cleaning.DataCleaning import DataCleaning

def test_normalize_floor():
    df = pd.DataFrame({
        'floor': ['სართ. 3', '8/11', '5', None, 'unknown']
    })

    cleaner = DataCleaning(df)
    cleaner._normalize_floor()

    expected = pd.Series(
        [3, 8, 5, pd.NA, pd.NA],
        name='floor',
        dtype='Int64'
    )

    pd.testing.assert_series_equal(
        cleaner.apartments_df['floor'],
        expected
    )
