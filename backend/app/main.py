from fastapi import FastAPI, HTTPException
import numpy as np
import pandas as pd
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from backend.app.schemas import PredictionRequest
from backend.app.state import SALE_MODEL, RENT_MODEL, SALE_SCHEMA, RENT_SCHEMA, SALE_DEFAULTS, RENT_DEFAULTS

# Run locally from backend/app:
# uvicorn backend.app.main:app --reload

app = FastAPI(title="Apartment Price Prediction API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/inference-data/{transaction_type}")
def get_inference_data(transaction_type: str):
    if transaction_type == "sale":
        return {
            "schema": SALE_SCHEMA,
            "defaults": SALE_DEFAULTS
        }
    elif transaction_type == "rent":
        return {
            "schema": RENT_SCHEMA,
            "defaults": RENT_DEFAULTS
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

@app.post("/api/predict")
def predict(req: PredictionRequest):
    """Returns predicted total price"""

    # --- select model
    if req.transaction_type == "sale":
        pipeline = SALE_MODEL
    elif req.transaction_type == "rent":
        pipeline = RENT_MODEL
    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # --- construct upload_date
    upload_date = datetime(
        year=req.year,
        month=req.month,
        day=15,
        hour=12,
        minute=0,
        second=0
    )

    # --- build input dataframe
    X = pd.DataFrame([{
        "city": req.city,
        "district_name": req.district,
        "area_m2": req.area_m2,
        "bedrooms": req.bedrooms,
        "floor": req.floor,
        "upload_date": upload_date
    }])

    try:
        pred_log = pipeline.predict(X)[0]
        prediction = round(float(np.expm1(pred_log)), 2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")

    return {
        "total_price": prediction
    }


@app.get("/")
def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "API is running"}
