import pandas as pd
import numpy as np


class FeatureEngineering:
    def __init__(self, sale_train, rent_train, sale_test, rent_test):
        self.sale_train = sale_train.copy()
        self.sale_test = sale_test.copy()

        self.rent_train = rent_train.copy()
        self.rent_test = rent_test.copy()

    def _apply_to_all(self, func):
        """ Helper function that applies the given function to all dataframes """
        for df_attr in ["sale_train", "rent_train", "sale_test", "rent_test"]:
            setattr(self, df_attr, func(getattr(self, df_attr)))

    def get_dfs(self):
        return self.sale_train, self.sale_test, self.rent_train, self.rent_test

    def __floor_buckets(self):
        """ Creates the following floor buckets: low, mid, high, very_high """
        def create_buckets(df):
            df["floor_bucket"] = pd.cut(
                df["floor"], bins=[-1, 2, 5, 10, 100], labels=["low", "mid", "high", "very_high"]
            ).astype(str)
            return df

        self._apply_to_all(create_buckets)

    def __area_buckets(self):
        """ Categorize apartments into area buckets such as studio, small, medium, large, very_large """
        def bucketize(df):
            df["area_bucket"] = pd.cut(
                df["area_m2"],
                bins=[0, 35, 60, 90, 130, float("inf")], labels=["studio", "small", "medium", "large", "very_large"]
            ).astype(str)
            return df

        self._apply_to_all(bucketize)

    def __area_per_bedroom(self):
        def calculate_area_per_bedroom(df):
            df["area_per_bedroom"] = round(df["area_m2"] / (df["bedrooms"] + 1), 2)
            return df

        self._apply_to_all(calculate_area_per_bedroom)

    def __group_districts(self, min_count=100):
        """Group rare districts into 'other' per city using TRAIN data only"""
        def fit_district_mapping(df):
            mapping = {}

            for city in df["city"].unique():
                counts = df[df["city"] == city]["district_name"].value_counts()
                valid_districts = counts[counts >= min_count].index
                mapping[city] = set(valid_districts)

            return mapping

        def apply_district_mapping(df, mapping):
            df["district_grouped"] = df["district_name"]

            for city, valid_set in mapping.items():
                mask = (df["city"] == city) & (~df["district_name"].isin(valid_set))
                df.loc[mask, "district_grouped"] = "other"

            return df

        # SALE
        sale_mapping = fit_district_mapping(self.sale_train)
        self.sale_train = apply_district_mapping(self.sale_train, sale_mapping)
        self.sale_test = apply_district_mapping(self.sale_test, sale_mapping)

        # RENT
        rent_mapping = fit_district_mapping(self.rent_train)
        self.rent_train = apply_district_mapping(self.rent_train, rent_mapping)
        self.rent_test = apply_district_mapping(self.rent_test, rent_mapping)

    def __city_district(self):
        def add(df):
            df = df.copy()
            df["city_district"] = df["city"] + "_" + df["district_grouped"]
            return df

        self._apply_to_all(add)

    def __district_median_price_per_sqm(self):
        """Add median price_per_sqm per (city, district_grouped) using TRAIN"""
        def compute_mapping(df):
            return (
                df.groupby(["city", "district_grouped"])["price_per_sqm"]
                .median().reset_index().rename(columns={"price_per_sqm": "district_median_price_per_sqm"})
            )

        def apply_mapping(df, mapping):
            mapping["district_median_price_per_sqm"] = mapping["district_median_price_per_sqm"].round(1)
            df = df.merge(mapping, on=["city", "district_grouped"], how="left")
            df["district_median_price_per_sqm"] = df["district_median_price_per_sqm"].fillna(df["price_per_sqm"])

            return df

        # --- SALE ---
        sale_mapping = compute_mapping(self.sale_train)
        self.sale_train = apply_mapping(self.sale_train, sale_mapping)
        self.sale_test = apply_mapping(self.sale_test, sale_mapping)

        # --- RENT ---
        rent_mapping = compute_mapping(self.rent_train)
        self.rent_train = apply_mapping(self.rent_train, rent_mapping)
        self.rent_test = apply_mapping(self.rent_test, rent_mapping)

    def __district_listing_count(self):
        """Add number of listings per (city, district_grouped)"""
        def compute_counts(df):
            return df.groupby(["city", "district_grouped"]).size().reset_index(name="district_listing_count")

        def apply_counts(df, counts):
            df = df.merge(counts, on=["city", "district_grouped"], how="left")
            df["district_listing_count"] = np.log1p(df["district_listing_count"])
            return df

        # --- SALE ---
        sale_counts = compute_counts(self.sale_train)
        self.sale_train = apply_counts(self.sale_train, sale_counts)
        self.sale_test = apply_counts(self.sale_test, sale_counts)

        # --- RENT ---
        rent_counts = compute_counts(self.rent_train)
        self.rent_train = apply_counts(self.rent_train, rent_counts)
        self.rent_test = apply_counts(self.rent_test, rent_counts)

    def __drop_unused_columns(self):
        DROP_ALWAYS = {
            "url",
            "description",
            "street_address",
            "source",
            "upload_date",
            "price_per_sqm",
            "district_name",
        }

        for df in [self.sale_train, self.sale_test, self.rent_train, self.rent_test]:
            df.drop(columns=DROP_ALWAYS, errors="ignore", inplace=True)

    def run(self):
        self.__floor_buckets()
        self.__area_buckets()
        self.__area_per_bedroom()
        self.__group_districts()
        self.__city_district()
        self.__district_median_price_per_sqm()
        self.__district_listing_count()

        self.__drop_unused_columns()

        self.sale_train.to_csv("data/sale_ml_apartments_processed.csv", index=False)
        self.rent_train.to_csv("data/rent_ml_apartments_processed.csv", index=False)
