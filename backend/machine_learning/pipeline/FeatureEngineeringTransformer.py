from sklearn.base import BaseEstimator, TransformerMixin
import pandas as pd
import numpy as np


class FeatureEngineeringTransformer(BaseEstimator, TransformerMixin):
    def __init__(self,):
        # learned attributes
        self.district_mapping = None
        self.median_mapping = None
        self.global_median = None
        self.count_mapping = None
        self.min_year = None

    # FIT (learn from TRAIN only)
    def fit(self, X, y=None):
        df = X.copy()

        # --- group districts
        self.district_mapping = {}
        for city in df["city"].unique():
            counts = df[df["city"] == city]["district_name"].value_counts()
            valid_districts = counts[counts >= 100].index
            self.district_mapping[city] = set(valid_districts)

        # apply grouping temporarily for next steps
        df["district_grouped"] = df["district_name"]
        for city, valid_set in self.district_mapping.items():
            mask = (df["city"] == city) & (~df["district_name"].isin(valid_set))
            df.loc[mask, "district_grouped"] = "other"

        # --- median price per sqm
        self.median_mapping = (df.groupby(["city", "district_grouped"])["price_per_sqm"].median())
        self.global_median = self.median_mapping.median()

        # --- listing count
        self.count_mapping = (df.groupby(["city", "district_grouped"]).size())

        # --- year normalization
        self.min_year = pd.to_datetime(df["upload_date"], errors="coerce").dt.year.min()

        return self

    # TRANSFORM (apply everywhere)
    def transform(self, X):
        df = X.copy()

        # --- floor buckets
        df["floor_bucket"] = pd.cut(
            df["floor"],
            bins=[-1, 2, 5, 10, 100],
            labels=["low", "mid", "high", "very_high"],
            right=False
        ).astype(str)

        # --- area buckets
        df["area_bucket"] = pd.cut(
            df["area_m2"],
            bins=[0, 35, 60, 90, 130, float("inf")],
            labels=["studio", "small", "medium", "large", "very_large"],
            right=False
        ).astype(str)

        # --- area per bedroom
        df["area_per_bedroom"] = df["area_m2"] / (df["bedrooms"] + 1)

        # --- group districts
        df["district_grouped"] = df["district_name"]
        for city, valid_set in self.district_mapping.items():
            mask = (df["city"] == city) & (~df["district_name"].isin(valid_set))
            df.loc[mask, "district_grouped"] = "other"

        # --- city_district
        df["city_district"] = df["city"] + "_" + df["district_grouped"]

        # --- median price per sqm
        idx = list(zip(df["city"], df["district_grouped"]))
        df["district_median_price_per_sqm"] = [self.median_mapping.get(k, self.global_median) for k in idx]
        df["district_median_price_per_sqm"] = df["district_median_price_per_sqm"].round(1)

        # --- listing count
        df["district_listing_count"] = [self.count_mapping.get(k, 0) for k in idx]
        df["district_listing_count"] = np.log1p(df["district_listing_count"])

        # --- extract year/month
        df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")
        df["upload_year"] = df["upload_date"].dt.year - self.min_year
        df["upload_month"] = df["upload_date"].dt.month

        # --- drop unused
        DROP_ALWAYS = {
            "url",
            "description",
            "street_address",
            "source",
            "upload_date",
            "price_per_sqm",
            "district_name",
            "transaction_type"
        }

        df.drop(columns=DROP_ALWAYS, errors="ignore", inplace=True)

        return df