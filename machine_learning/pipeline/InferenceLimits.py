import pandas as pd
import numpy as np
import os, json


class InferenceLimits:
    def __init__(self, train_df, val_df, transaction_type, base_dir):
        self.df = pd.concat([train_df, val_df])
        self.transaction_type = transaction_type
        self.base_dir = base_dir
        self.schema = {}

    def build_city_districts(self):
        """Build cities list and mapping: city -> districts"""
        df = self.df.copy()

        df = df.dropna(subset=["city", "district_name"])  # Ensure no NaNs
        self.schema["cities"] = sorted(df["city"].unique().tolist())  # cities list

        # mapping: city -> districts
        self.schema["city_districts"]  = (
            df.groupby("city")["district_name"].unique()
            .apply(lambda x: sorted(x.tolist())).to_dict()
        )

    def get_area_m2_limits(self):
        """ Get area m2 hard limits based on min and max, and soft limits based on quantile """
        df = self.df.copy()
        self.schema["area_m2"] = {
            "hard_min": int(np.floor(df["area_m2"].min())),
            "hard_max": int(np.ceil(df["area_m2"].max())),
            "soft_min": int(np.floor(df["area_m2"].quantile(0.01))),
            "soft_max": int(np.ceil(df["area_m2"].quantile(0.99))),
        }

    def get_bedrooms_limits(self):
        df = self.df.copy()
        self.schema["bedrooms"] = {
            "hard_min": 0,
            "hard_max": int(df["bedrooms"].max()),
        }

    def get_floor_limits(self):
        """ Compute floor limits: global hard bounds + city-based soft upper bounds """
        df = self.df.copy()

        # --- City-based soft upper limits (p99)
        city_upper_bounds = {}

        for city in df["city"].dropna().unique():
            city_df = df[df["city"] == city]

            if len(city_df) == 0:
                continue

            upper = city_df["floor"].max()

            city_upper_bounds[city] = int(round(upper))

        # --- Save into schema
        self.schema["floor"] = {
            "hard_min": 0,
            "hard_max": 60,
            "soft_max_by_city": city_upper_bounds
        }

    def get_upload_date_limits(self):
        """ Build year list and year -> available months mapping """
        df = self.df.copy()

        # Ensure datetime
        df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")

        # Drop invalid dates
        df = df.dropna(subset=["upload_date"])

        # Extract year and month
        df["year"] = df["upload_date"].dt.year.astype(int)
        df["month"] = df["upload_date"].dt.month.astype(int)

        # --- Unique sorted years
        years = sorted(df["year"].unique().tolist())

        # --- Mapping: year -> months
        year_month_map = (
            df.groupby("year")["month"].unique()
            .apply(lambda x: sorted(x.tolist())).to_dict()
        )

        # Save into schema
        self.schema["upload_date"] = {
            "years": years,
            "year_month_map": year_month_map
        }

    def build_defaults(self):
        """ Build default schema with default values """
        max_year = max(self.schema["upload_date"]["years"])
        months = self.schema["upload_date"]["year_month_map"][max_year]

        self.schema["defaults"] = {"bedrooms": 2, "floor": 3, "year": max_year, "month": max(months)}

    def save(self):
        """ Saves schema into base_dir directory creating name based on transaction type """
        os.makedirs(self.base_dir, exist_ok=True)  # Create directory if not exists

        filename = f"{self.transaction_type}_inference_data.json"  # Build filename
        filepath = os.path.join(self.base_dir, filename)

        with open(filepath, "w") as f:
            json.dump(self.schema, f, indent=2, sort_keys=True, default=float, ensure_ascii=False)

    def run(self):
        """ Main function to create JSON schema """
        self.build_city_districts()
        self.get_area_m2_limits()
        self.get_bedrooms_limits()
        self.get_floor_limits()
        self.get_upload_date_limits()
        self.build_defaults()

        self.save()
