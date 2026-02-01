import joblib
import numpy as np
import pandas as pd
from pathlib import Path


class LocalPricePredictor:
    """Loads trained model and inference metadata and predicts apartment prices"""

    def __init__(self, model_path, artifacts_dir="models"):
        artifacts_dir = Path(artifacts_dir)

        # Load trained model bundle
        model_data = joblib.load(model_path)
        self.pipeline = model_data["pipeline"]
        self.target = model_data["target"]

        # Load all inference metadata (single source of truth)
        meta = joblib.load(artifacts_dir / "inference_metadata.joblib")

        self.district_group_map = meta["district_group_map"]

        self.district_median = meta["district_stats"]["median_price_per_sqm"]
        self.district_count = meta["district_stats"]["listing_count"]

        self.floor_bins = meta["preprocessing_config"]["floor_bins"]
        self.floor_labels = meta["preprocessing_config"]["floor_labels"]

        self.available_dates = meta["available_dates"]
        self.validation_bounds = meta["validation_bounds"]

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
        """Predicts price_per_sqm or price for a single apartment"""

        # Map raw district to grouped district
        district_grouped = self.district_group_map.get((city, district), "other")

        # District-level fallback features
        price_median = self.district_median.get((city, district_grouped), np.nan)
        listing_count = self.district_count.get((city, district_grouped), np.nan)

        # Convert floor to categorical bucket
        floor_bucket = pd.cut(
            [floor],
            bins=self.floor_bins,
            labels=self.floor_labels
        )[0]

        # Build single-row feature frame (must match training schema)
        X = pd.DataFrame([{
            "city": city,
            "district_grouped": district_grouped,
            "area_m2": area_m2,
            "bedrooms": bedrooms,
            "floor": floor,
            "upload_year": year,
            "upload_month": month,
            "floor_bucket": floor_bucket,
            "price_per_sqm_district_median": price_median,
            "district_listing_count": listing_count,
        }])

        # Model predicts log-space target → invert transform
        pred_log = self.pipeline.predict(X)[0]
        return float(np.expm1(pred_log))
