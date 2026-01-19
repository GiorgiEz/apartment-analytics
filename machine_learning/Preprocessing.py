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
        """ Removes area_m2 values that are too high """
        self.apartments_df = self.apartments_df[
            (self.apartments_df["area_m2"] >= 15) &
            (self.apartments_df["area_m2"] <= 500)
            ]

    def __remove_extreme_price_values(self):
        """Removes extreme price values for sale and monthly rent apartments"""

        df = self.apartments_df

        def clean_prices(df, transaction_type, price_col, min_price):
            """Generic price cleaner"""

            mask = df["transaction_type"] == transaction_type
            sub_df = df.loc[mask].copy()

            # Step 1: Hard sanity filters
            sub_df = sub_df[(sub_df["area_m2"] >= 15) & (sub_df[price_col] >= min_price)]

            # Step 2: IQR filtering (city + district)
            grp = sub_df.groupby(["city", "district_grouped"])[price_col]

            q1 = grp.transform("quantile", 0.25)
            q3 = grp.transform("quantile", 0.75)
            iqr = q3 - q1

            sub_df = sub_df[(sub_df[price_col] >= q1 - 1.5 * iqr) & (sub_df[price_col] <= q3 + 3.0 * iqr)]

            # Step 3: Winsorization
            low = grp.transform(lambda x: x.quantile(0.05))
            high = grp.transform(lambda x: x.quantile(0.95))

            sub_df = sub_df.assign(
                **{
                    price_col: sub_df[price_col]
                    .clip(low, high)
                    .round(2)
                }
            )

            return sub_df

        # Clean sale prices (price_per_sqm)
        sale_df = clean_prices(df=df, transaction_type="იყიდება", price_col="price_per_sqm", min_price=150)

        # Clean monthly rent prices (price)
        rent_df = clean_prices(df=df, transaction_type="ქირავდება თვიურად", price_col="price", min_price=100)

        # Merge back
        df = pd.concat(
            [
                df.loc[
                    ~df["transaction_type"].isin(
                        ["იყიდება", "ქირავდება თვიურად"]
                    )
                ],
                sale_df,
                rent_df
            ],
            ignore_index=True
        )

        self.apartments_df = df

    def __group_districts_by_frequency(self, min_count=100):
        """ Only leaves districts with 100+ listings, groups others into 'other' """
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
        """ Extracts upload year and upload month as separate columns, normalizes upload year to 0 """
        self.apartments_df["upload_year"] = self.apartments_df["upload_date"].dt.year
        self.apartments_df["upload_year"] -= self.apartments_df["upload_year"].min()

        self.apartments_df["upload_month"] = self.apartments_df["upload_date"].dt.month

    def __handle_floor(self):
        """Imputes missing floors with city-wise median and creates new column for floor buckets """
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
        """Creates new price_per_sqm_median by districts """
        med = self.apartments_df.groupby(["city", "district_grouped"])["price_per_sqm"].median()
        self.apartments_df = self.apartments_df.join(med, on=["city", "district_grouped"], rsuffix="_district_median")

    def __district_listing_count(self):
        """Creates new listing count column by districts """
        counts = self.apartments_df.groupby(["city", "district_grouped"]).size()
        self.apartments_df["district_listing_count"] = (
            self.apartments_df.set_index(["city", "district_grouped"]).index.map(counts))

    def __drop_unused_columns(self):
        """Drops unnecessary columns for ML from apartments_df """
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
        """ Saves necessary data for prediction models """
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
        """ Main method to run Preprocessing tasks before model training """
        # Main preprocessing
        self.__remove_extreme_areas()
        self.__group_districts_by_frequency()
        self.__remove_extreme_price_values()
        self.__extract_year_and_month()
        self.__handle_floor()
        self.__price_per_sqm_median_by_districts()
        self.__district_listing_count()

        # Save inference artifacts
        self.__save_inference_artifacts(output_dir="models")

        self.__drop_unused_columns()
        self.apartments_df.to_csv("data/ml_apartments_processed.csv", index=False)
