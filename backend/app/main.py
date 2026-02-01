from fastapi import FastAPI
import numpy as np
import pandas as pd
from schemas import PredictionRequest
from fastapi.middleware.cors import CORSMiddleware
from state import (
    SALE_MODEL, RENT_MODEL, DISTRICT_GROUP_MAP, ALLOWED_CITIES, DISTRICTS_BY_CITY,
    DISTRICT_MEDIAN, DISTRICT_COUNT, PREPROCESSING_CONFIG, AVAILABLE_DATES, VALIDATION_BOUNDS, DEFAULTS
)

# Run locally from backend/app:
# uvicorn main:app --reload

app = FastAPI(title="Apartment Price Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/predict")
def predict(req: PredictionRequest):
    """ Returns predicted price_per_sqm, total sale price, and monthly rent """

    # Load trained pipelines
    sale_pipeline = SALE_MODEL["pipeline"]
    rent_pipeline = RENT_MODEL["pipeline"]

    # Map raw district to grouped district used in training and load District-level fallback features
    district_grouped = DISTRICT_GROUP_MAP.get((req.city, req.district), "other")
    median = DISTRICT_MEDIAN.get((req.city, district_grouped), np.nan)
    count = DISTRICT_COUNT.get((req.city, district_grouped), np.nan)

    # Convert floor to categorical bucket
    floor_bucket = pd.cut(
        [req.floor],
        bins=PREPROCESSING_CONFIG["floor_bins"],
        labels=PREPROCESSING_CONFIG["floor_labels"]
    )[0]

    # Build single-row feature frame
    X = pd.DataFrame([{
        "city": req.city,
        "district_grouped": district_grouped,
        "area_m2": req.area_m2,
        "bedrooms": req.bedrooms,
        "floor": req.floor,
        "upload_year": req.year,
        "upload_month": req.month,
        "floor_bucket": floor_bucket,
        "price_per_sqm_district_median": median,
        "district_listing_count": count,
    }])

    # Predict in log-space and invert transform
    sale_prediction = round(float(np.expm1(sale_pipeline.predict(X)[0])), 2)
    rent_prediction = round(float(np.expm1(rent_pipeline.predict(X)[0])), 2)

    return {
        "price_per_sqm": sale_prediction,
        "total_price": sale_prediction * req.area_m2,
        "monthly_rent": rent_prediction
    }


@app.get("/api/model/metadata")
def get_model_metadata():
    return {
        "cities": ALLOWED_CITIES,
        "districts_by_city": DISTRICTS_BY_CITY,
        "validation_bounds": VALIDATION_BOUNDS,
        "available_dates": AVAILABLE_DATES,
        "defaults": DEFAULTS
    }


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is running"}
