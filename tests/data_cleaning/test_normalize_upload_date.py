import pandas as pd
from datetime import datetime
from data_cleaning import DataCleaning


# Assumption: upload timestamps must not be in the future.
# Partial dates resolving to future datetimes are rolled back one year.
def test_normalize_upload_date():
    now = datetime(2026, 1, 1, 10, 0)

    df = pd.DataFrame({
        'upload_date': [
            '1 წუთის წინ',
            '23 საათის წინ',
            '30 დეკ, 12:02',
            '01 იან 08:44',
            '01 იან 12:44',
            '01 იან 2026',
            '2026-12-29 15:21:00',
            '2025-12-29 15:21'
        ]
    })

    cleaner = DataCleaning(df)
    cleaner._normalize_upload_date(now=now)

    result = cleaner.apartments_df['upload_date']

    expected = pd.Series(
        [
            datetime(2026, 1, 1, 9, 59),
            datetime(2025, 12, 31, 11, 0),
            datetime(2025, 12, 30, 12, 2),
            datetime(2026, 1, 1, 8, 44),
            datetime(2025, 1, 1, 12, 44),
            datetime(2026, 1, 1, 12, 0),
            datetime(2025, 12, 29, 15, 21),
            datetime(2025, 12, 29, 15, 21),
        ],
        name='upload_date',
        dtype='datetime64[ns]'
    )

    pd.testing.assert_series_equal(result, expected)
