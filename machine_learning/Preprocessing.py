import pandas as pd
import joblib
import json
from pathlib import Path



class Preprocessing:
    def __init__(self, apartments_df):
        self.apartments_df = apartments_df[
            apartments_df["transaction_type"].isin(["იყიდება", "ქირავდება თვიურად"])
        ].copy()

    def __remove_extreme_areas(self):
        self.apartments_df = self.apartments_df[self.apartments_df["area_m2"] <= 700]

    def __remove_extreme_prices(self):
        # Sale
        sale_mask = self.apartments_df["transaction_type"] == "იყიდება"
        q_sale = self.apartments_df.loc[sale_mask, "price_per_sqm"].quantile(0.995)
        self.apartments_df = self.apartments_df[
            ~sale_mask | (self.apartments_df["price_per_sqm"] <= q_sale)
            ]

        # Monthly rent
        rent_mask = self.apartments_df["transaction_type"] == "ქირავდება თვიურად"
        q_rent = self.apartments_df.loc[rent_mask, "price"].quantile(0.995)
        self.apartments_df = self.apartments_df[
            ~rent_mask | (self.apartments_df["price"] <= q_rent)
            ]

    def __group_districts_by_frequency(self, min_count=100):
        grouped = []

        for city, city_df in self.apartments_df.groupby("city", sort=False):
            freq = city_df["district_name"].value_counts()
            keep = freq[freq >= min_count].index

            city_df["district_grouped"] = city_df["district_name"].where(
                city_df["district_name"].isin(keep),
                "other"
            )

            grouped.append(city_df)

        self.apartments_df = pd.concat(grouped).reset_index(drop=True)

    def __extract_year_and_month(self):
        self.apartments_df["upload_year"] = self.apartments_df["upload_date"].dt.year
        self.apartments_df["upload_year"] -= self.apartments_df["upload_year"].min()

        self.apartments_df["upload_month"] = self.apartments_df["upload_date"].dt.month

    def __handle_floor(self):
        # impute missing floors with city-wise median
        self.apartments_df["floor"] = (
            self.apartments_df
            .groupby("city")["floor"]
            .transform(lambda s: s.fillna(s.median()))
        )

        self.apartments_df["floor_bucket"] = pd.cut(
            self.apartments_df["floor"],
            bins=[-1, 0, 2, 5, 10, 20, 100],
            labels=["basement", "low", "mid", "high", "very_high", "skyscraper"]
        )

    def __price_per_sqm_median_by_districts(self):
        med = self.apartments_df.groupby(["city", "district_grouped"])["price_per_sqm"].median()
        self.apartments_df = self.apartments_df.join(med, on=["city", "district_grouped"], rsuffix="_district_median")

    def __district_listing_count(self):
        counts = self.apartments_df.groupby(["city", "district_grouped"]).size()
        self.apartments_df["district_listing_count"] = self.apartments_df.set_index(["city", "district_grouped"]).index.map(counts)

    def __drop_unused_columns(self):
        DROP_ALWAYS = {
            "url",
            "description",
            "street_address",
            "district_name",
            "source",
            'upload_date'
        }

        self.apartments_df.drop(columns=DROP_ALWAYS, errors="ignore", inplace=True)

    def __save_inference_artifacts(self, output_dir="models"):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. District → grouped district mapping
        district_map = (
            self.apartments_df[["city", "district_name", "district_grouped"]]
            .drop_duplicates()
            .set_index(["city", "district_name"])["district_grouped"]
            .to_dict()
        )

        joblib.dump(district_map, output_dir / "district_group_map.joblib")

        # 2. District statistics
        district_median = (
            self.apartments_df
            .groupby(["city", "district_grouped"])["price_per_sqm"]
            .median()
            .to_dict()
        )

        district_count = (
            self.apartments_df
            .groupby(["city", "district_grouped"])
            .size()
            .to_dict()
        )

        joblib.dump(
            {
                "median_price_per_sqm": district_median,
                "listing_count": district_count
            },
            output_dir / "district_stats.joblib"
        )

        # 3. Preprocessing config (floor bins, labels, year normalization)
        preprocessing_config = {
            "floor_bins": [-1, 0, 2, 5, 10, 20, 100],
            "floor_labels": ["basement", "low", "mid", "high", "very_high", "skyscraper"],
            "min_upload_year": int(self.apartments_df["upload_date"].dt.year.min())
        }

        joblib.dump(preprocessing_config, output_dir / "preprocessing_config.joblib")

        # 4. Available (year → months)
        available_dates = (
            self.apartments_df
            .groupby("upload_year")["upload_month"]
            .apply(lambda s: sorted(int(m) for m in s.unique()))
        )

        available_dates = {
            int(year) + int(preprocessing_config["min_upload_year"]): months
            for year, months in available_dates.items()
        }

        with open(output_dir / "available_dates.json", "w", encoding="utf-8") as f:
            json.dump(available_dates, f, ensure_ascii=False)

    def run(self):
        self.__remove_extreme_areas()
        self.__remove_extreme_prices()
        self.__group_districts_by_frequency()
        self.__extract_year_and_month()
        self.__handle_floor()
        self.__price_per_sqm_median_by_districts()
        self.__district_listing_count()

        # Save inference artifacts
        self.__save_inference_artifacts(output_dir="models")

        self.__drop_unused_columns()
        self.apartments_df.to_csv("data/ml_apartments_processed.csv", index=False)
