import json
import joblib
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# ML models
sale_model = joblib.load(MODELS_DIR / "sale_price_per_sqm.joblib")
rent_model = joblib.load(MODELS_DIR / "rent_price.joblib")

# Metadata
district_group_map = joblib.load(MODELS_DIR / "district_group_map.joblib")

district_stats = joblib.load(MODELS_DIR / "district_stats.joblib")
district_median = district_stats["median_price_per_sqm"]
district_count = district_stats["listing_count"]

preprocessing_config = joblib.load(
    MODELS_DIR / "preprocessing_config.joblib"
)

with open(MODELS_DIR / "available_dates.json", "r", encoding="utf-8") as f:
    available_dates = {
        int(year): months for year, months in json.load(f).items()
    }
