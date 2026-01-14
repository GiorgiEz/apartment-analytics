import pandas as pd
import numpy as np


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
        self.apartments_df["month_sin"] = np.sin(2 * np.pi * self.apartments_df["upload_month"] / 12)
        self.apartments_df["month_cos"] = np.cos(2 * np.pi * self.apartments_df["upload_month"] / 12)

        self.apartments_df.drop(columns=["upload_month"], inplace=True)

    def __handle_floor(self):
        # impute missing floors with city-wise median
        self.apartments_df["floor"] = (
            self.apartments_df
            .groupby("city")["floor"]
            .transform(lambda s: s.fillna(s.median()))
        )

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

    def run(self):
        self.__remove_extreme_areas()
        self.__remove_extreme_prices()
        self.__group_districts_by_frequency()
        self.__extract_year_and_month()
        self.__handle_floor()

        self.__drop_unused_columns()
        self.apartments_df.to_csv("data/ml_apartments_processed.csv", index=False)
