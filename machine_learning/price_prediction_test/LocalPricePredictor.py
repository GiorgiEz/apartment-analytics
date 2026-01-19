import joblib
import numpy as np
import pandas as pd
from pathlib import Path


class LocalPricePredictor:
    """Loads trained artifacts and predicts price_per_sqm for a single apartment"""

    def __init__(self, model_path, artifacts_dir = "models"):
        # Load trained model bundle (pipeline + target info)
        artifacts_dir = Path(artifacts_dir)
        data = joblib.load(model_path)

        self.pipeline = data["pipeline"]
        self.target = data["target"]

        # Load minimal artifacts
        self.district_group_map = joblib.load(artifacts_dir / "district_group_map.joblib")

        stats = joblib.load(artifacts_dir / "district_stats.joblib")
        self.district_median = stats["median_price_per_sqm"]
        self.district_count = stats["listing_count"]

        # Preprocessing configuration (shared with training)
        config = joblib.load(artifacts_dir / "preprocessing_config.joblib")
        self.floor_bins = config["floor_bins"]
        self.floor_labels = config["floor_labels"]

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

        district_grouped = self.district_group_map.get((city, district), "other")
        price_median = self.district_median.get((city, district_grouped), np.nan)
        listing_count = self.district_count.get((city, district_grouped), np.nan)
        floor_bucket = pd.cut([floor], bins=self.floor_bins, labels=self.floor_labels)[0]

        # Build single-row feature frame (must match training schema)
        X = pd.DataFrame([{
            "city": city,
            "district_grouped": district_grouped,
            "area_m2": area_m2,
            "bedrooms": bedrooms,
            "floor": floor,
            "upload_year": year,
            "upload_month": month,

            # loaded / derived
            "floor_bucket": floor_bucket,
            "price_per_sqm_district_median": price_median,
            "district_listing_count": listing_count,
        }])

        # Model predicts log(price_per_sqm); invert transform
        pred_log = self.pipeline.predict(X)[0]
        return float(np.expm1(pred_log))
