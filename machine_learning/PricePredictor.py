import joblib
import numpy as np
import pandas as pd


class PricePredictor:
    def __init__(self, model_path: str):
        data = joblib.load(model_path)

        self.pipeline = data["pipeline"]
        self.target = data["target"]

    def predict_single(
        self,
        *,
        city: str,
        district: str,
        area_m2: float,
        bedrooms: int,
        floor: int,
        year: int,
        month: int,
    ) -> float:

        floor_bucket = pd.cut(
            [floor],
            bins=[-1, 0, 2, 5, 10, 20, 100],
            labels=["basement", "low", "mid", "high", "very_high", "skyscraper"]
        )[0]

        X = pd.DataFrame([{
            "city": city,
            "district_grouped": district,
            "area_m2": area_m2,
            "bedrooms": bedrooms,
            "floor": floor,
            "upload_year": year,
            "upload_month": month,
            "floor_bucket": floor_bucket,
            "price_per_sqm_district_median": np.nan,
            "district_listing_count": np.nan,
        }])

        pred_log = self.pipeline.predict(X)[0]
        return float(np.expm1(pred_log))
