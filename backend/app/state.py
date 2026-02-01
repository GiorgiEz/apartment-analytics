# state.py

import joblib
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

""" 1. ML MODELS """
SALE_MODEL = joblib.load(MODELS_DIR / "sale_price_per_sqm.joblib")
RENT_MODEL = joblib.load(MODELS_DIR / "rent_price.joblib")

""" 2. INFERENCE METADATA """
META = joblib.load(MODELS_DIR / "inference_metadata.joblib")

""" 3. CITY-DISTRICT MAPPING """
DISTRICT_GROUP_MAP = META["district_group_map"]

ALLOWED_CITIES = sorted({city for city, _ in DISTRICT_GROUP_MAP.keys()})

districts_by_city = {}
for city, district in DISTRICT_GROUP_MAP.keys():
    if not isinstance(district, str):
        continue
    districts_by_city.setdefault(city, set()).add(district.strip())

DISTRICTS_BY_CITY = {city: sorted(districts) for city, districts in districts_by_city.items()}

""" 4. DISTRICT-LEVEL STATISTICS """
DISTRICT_MEDIAN = META["district_stats"]["median_price_per_sqm"]
DISTRICT_COUNT = META["district_stats"]["listing_count"]

""" 5. PREPROCESSING CONFIGURATION """
PREPROCESSING_CONFIG = META["preprocessing_config"]

""" 6. AVAILABLE YEAR AND MONTHS """
AVAILABLE_DATES = META["available_dates"]

""" 7. BOUND VALIDATIONS (area_m2, bedrooms, floor) """
VALIDATION_BOUNDS = META.get("validation_bounds")

""" 8. DEFAULT VALUES """
LATEST_YEAR = max(int(year) for year in AVAILABLE_DATES.keys())
LATEST_MONTH = max(int(m) for m in AVAILABLE_DATES[LATEST_YEAR])

DEFAULTS = {
    "bedrooms": 2,
    "floor": 3,
    "year": LATEST_YEAR,
    "month": LATEST_MONTH,
}
