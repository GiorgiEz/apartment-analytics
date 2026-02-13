import pandas as pd
from data_cleaning import NormalizeDistricts


def test_normalize_districts_from_street_mapping():
    df = pd.DataFrame({
        "city": ["ქუთაისი", "ქუთაისი", "ქუთაისი"],
        "district_name": [None, None, None],
        "street_address": [
            "გამარჯვების III შეს.",
            "განჯის ქუჩა",
            "მ. ლებანიძის ქუჩა",
        ],
    })

    cleaner = NormalizeDistricts(df)
    cleaner.normalize_non_tbilisi_districts()

    result = cleaner.apartments_df["district_name"].tolist()

    expected = [
        "აღმაშენებელი",
        "ბალახვანი",
        "გორა",
    ]

    assert result == expected
