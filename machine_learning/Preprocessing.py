import pandas as pd
import joblib
from pathlib import Path



class Preprocessing:
    def __init__(self, sale_train, rent_train, sale_test, rent_test):
        self.sale_train = sale_train
        self.sale_test = sale_test

        self.rent_train = rent_train
        self.rent_test = rent_test

    def __remove_extreme_areas(self):
        """ Removes area_m2 values that are too high or low"""
        self.sale_train = self.sale_train[(self.sale_train["area_m2"] >= 15) & (self.sale_train["area_m2"] <= 500)]
        self.sale_test = self.sale_test[(self.sale_test["area_m2"] >= 15) & (self.sale_test["area_m2"] <= 500)]

        self.rent_train = self.rent_train[(self.rent_train["area_m2"] >= 15) & (self.rent_train["area_m2"] <= 500)]
        self.rent_test = self.rent_test[(self.rent_test["area_m2"] >= 15) & (self.rent_test["area_m2"] <= 500)]

    def __remove_extreme_prices(self):
        """ Removes extreme price values for sale and monthly rent apartments """

        def clean_prices(train, test, min_price):
            price_col = "price"

            # remove impossible prices
            train = train[train[price_col] >= min_price]
            test = test[test[price_col] >= min_price]

            # compute bounds from train
            grp = train.groupby(["city", "district_name"])[price_col]

            bounds = grp.quantile([0.25, 0.75]).unstack()
            bounds.columns = ["q1", "q3"]

            bounds["iqr"] = bounds["q3"] - bounds["q1"]
            bounds["lower"] = bounds["q1"] - 1.5 * bounds["iqr"]
            bounds["upper"] = bounds["q3"] + 1.5 * bounds["iqr"]

            bounds = bounds.reset_index()

            # apply to train
            train = train.merge(bounds, on=["city", "district_name"], how="left")
            train = train[(train[price_col] >= train["lower"]) & (train[price_col] <= train["upper"])]
            train = train.drop(columns=["q1", "q3", "iqr", "lower", "upper"])

            # apply to test
            test = test.merge(bounds, on=["city", "district_name"], how="left")
            test = test[(test[price_col] >= test["lower"]) & (test[price_col] <= test["upper"])]
            test = test.drop(columns=["q1", "q3", "iqr", "lower", "upper"])

            return train, test

        self.sale_train, self.sale_test = clean_prices(self.sale_train, self.sale_test, min_price=5000)
        self.rent_train, self.rent_test = clean_prices(self.rent_train, self.rent_test, min_price=50)

    def __extract_year_and_month(self):
        """Extract year and month, normalize year using train minimum"""

        def extract(df, min_year):
            df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")

            df["upload_year"] = df["upload_date"].dt.year - min_year
            df["upload_month"] = df["upload_date"].dt.month

        # compute rule from train
        sale_min_year = pd.to_datetime(self.sale_train["upload_date"], errors='coerce').dt.year.min()
        rent_min_year = pd.to_datetime(self.rent_train["upload_date"], errors='coerce').dt.year.min()

        # apply to train
        extract(self.sale_train, sale_min_year)
        extract(self.rent_train, rent_min_year)

        # apply same rule to test
        extract(self.sale_test, sale_min_year)
        extract(self.rent_test, rent_min_year)

    def __drop_unused_columns(self):
        DROP_ALWAYS = {
            "url",
            "description",
            "street_address",
            "source",
            "upload_date",
            "price_per_sqm"
        }

        for df in [self.sale_train, self.sale_test, self.rent_train, self.rent_test]:
            df.drop(columns=DROP_ALWAYS, errors="ignore", inplace=True)

    def __save_inference_artifacts(self, output_dir="models"):
        """ Saves all artifacts required for inference """

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Available dates (year → months)
        def get_available_dates(df):
            available_dates = (
                df
                .groupby("upload_year")["upload_month"]
                .apply(lambda s: sorted(int(m) for m in s.unique()))
                .to_dict()
            )
            min_upload_year = int(df["upload_year"].min())
            return {int(year) + min_upload_year: sorted(months) for year, months in available_dates.items()}

        rent_available_dates = get_available_dates(self.rent_train)
        sale_available_dates = get_available_dates(self.sale_train)

        # Validation bounds (data-driven limits)
        def get_validation_bounds(df):
            return {
                "area_m2": {
                    "min": float(df["area_m2"].quantile(0.01)),
                    "max": float(df["area_m2"].quantile(0.99)),
                },
                "bedrooms": {
                    "min": int(df["bedrooms"].min()),
                    "max": int(df["bedrooms"].max()),
                },
                "floor": {
                    "min": int(df["floor"].quantile(0.01)),
                    "max": int(df["floor"].quantile(0.99)),
                }
            }

        rent_validation_bounds = get_validation_bounds(self.rent_train)
        sale_validation_bounds = get_validation_bounds(self.sale_train)

        # Save everything in one artifact
        rent_inference_metadata = {
            "available_dates": rent_available_dates,
            "validation_bounds": rent_validation_bounds,
        }

        sale_inference_metadata = {
            "available_dates": sale_available_dates,
            "validation_bounds": sale_validation_bounds,
        }

        joblib.dump(rent_inference_metadata, output_dir / "rent_inference_metadata.joblib")
        joblib.dump(sale_inference_metadata, output_dir / "sale_inference_metadata.joblib")

    def run(self):
        """ Main method to run Preprocessing tasks before model training """
        # Main preprocessing
        self.__remove_extreme_areas()
        self.__remove_extreme_prices()
        self.__extract_year_and_month()

        # Save inference artifacts
        self.__save_inference_artifacts(output_dir="models")

        self.__drop_unused_columns()
        self.sale_train.to_csv("data/sale_ml_apartments_processed.csv", index=False)
        self.rent_train.to_csv("data/rent_ml_apartments_processed.csv", index=False)
