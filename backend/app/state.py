# state.py

import joblib, json
from pathlib import Path

# Defines directory paths
TRAINED_MODELS_DIR = Path(__file__).resolve().parent.parent / "machine_learning/trained_models"
INFERENCE_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "inference_schema"


# Load models and inference data
def load_model(name):
    return joblib.load(TRAINED_MODELS_DIR / name)

def load_schema(name):
    with open(INFERENCE_SCHEMA_DIR / name, encoding="utf-8") as f:
        return json.load(f)

try:
    SALE_MODEL = load_model("RandomForestRegressor_Sale.joblib")
    RENT_MODEL = load_model("RandomForestRegressor_Rent.joblib")
except Exception as e:
    raise RuntimeError(f"Failed to load model: {e}")

try:
    SALE_SCHEMA = load_schema("Sale_inference_data.json")
    RENT_SCHEMA = load_schema("Rent_inference_data.json")
except Exception as e:
    raise RuntimeError(f"Failed to load schema: {e}")
