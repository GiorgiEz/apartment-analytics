from fastapi import FastAPI
import numpy as np
import pandas as pd
from schemas import PredictionRequest
from fastapi.middleware.cors import CORSMiddleware
from state import (
    sale_model,
    rent_model,
    district_group_map,
    district_median,
    district_count,
    preprocessing_config,
    available_dates
)

# inside backend/app -> run "uvicorn main:app --reload"

app = FastAPI(title="Apartment Price Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/predict")
def predict(req: PredictionRequest):

    sale_pipeline = sale_model["pipeline"]
    rent_pipeline = rent_model["pipeline"]

    district_grouped = district_group_map.get((req.city, req.district), "other")
    median = district_median.get((req.city, district_grouped), np.nan)
    count = district_count.get((req.city, district_grouped), np.nan)

    floor_bucket = pd.cut(
        [req.floor],
        bins=preprocessing_config["floor_bins"],
        labels=preprocessing_config["floor_labels"]
    )[0]

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

    sale_prediction = round(float(np.expm1(sale_pipeline.predict(X)[0])), 2)
    rent_prediction = round(float(np.expm1(rent_pipeline.predict(X)[0])), 2)

    return {
        "price_per_sqm": sale_prediction,
        "total_price": sale_prediction * req.area_m2,
        "monthly_rent": rent_prediction
    }

@app.get("/api/available-dates")
def get_available_dates():
    return available_dates

@app.get("/api/cities")
def get_cities():
    cities = sorted({city for city, _ in district_group_map.keys()})
    return cities

@app.get("/api/districts/{city}")
def get_districts(city: str):
    city = city.strip()

    districts = sorted({
        str(district).strip()
        for (c, district) in district_group_map.keys()
        if c == city and isinstance(district, str)
    })

    return districts

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}
