import joblib
import numpy as np
import pandas as pd


class LocalPricePredictor:
    """Loads trained model and inference metadata and predicts apartment prices"""

    def __init__(self):
        # Load trained model bundle
        sale_model_data = joblib.load("../models/sale_prediction.joblib")
        self.sale_pipeline = sale_model_data

        rent_model_data = joblib.load("../models/rent_prediction.joblib")
        self.rent_pipeline = rent_model_data

    def predict_single(self, *, city: str, district: str, area_m2: float,
                       bedrooms: int, floor: int, year: int, month: int) -> dict[str, float]:
        """Predicts price_per_sqm or price for a single apartment"""

        # Build single-row feature frame (must match training schema)
        X = pd.DataFrame([{
            "city": city,
            "district_name": district,
            "area_m2": area_m2,
            "bedrooms": bedrooms,
            "floor": floor,
            "upload_year": year,
            "upload_month": month,
        }])

        # Model predicts log-space target → invert transform
        sale_pred_log = self.sale_pipeline.predict(X)[0]
        rent_pred_log = self.rent_pipeline.predict(X)[0]

        return {
            "sale_price": round(float(np.expm1(sale_pred_log)), 2),
            "rent_price": round(float(np.expm1(rent_pred_log)), 2)
        }
