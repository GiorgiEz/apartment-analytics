from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from pathlib import Path
import pandas as pd
import numpy as np


class PriceModel:
    def __init__(self, df, target):
        self.df = df.copy()
        self.target = target

        if target not in {"price", "price_per_sqm"}:
            raise ValueError("target must be 'price' or 'price_per_sqm'")

        self._prepare_data()

    def _prepare_data(self):
        # Drop leakage column
        leakage_col = "price_per_sqm" if self.target == "price" else "price"
        self.df.drop(columns=[leakage_col], inplace=True)

        # Drop rows with missing target
        self.df = self.df.dropna(subset=[self.target])

        # Sort only for reproducibility (NOT for splitting logic)
        self.df = self.df.sort_values(
            ["upload_year", "upload_month"]
        ).reset_index(drop=True)

        # Log-transform target
        self.y = np.log1p(self.df[self.target])
        self.X = self.df.drop(columns=[self.target])

    def build_pipeline(self):
        numeric_features = [
            "area_m2",
            "bedrooms",
            "floor",
            "upload_year",
            "upload_month",
            "price_per_sqm_district_median",
            "district_listing_count"
        ]

        categorical_features = [
            "city",
            "district_grouped",
            "floor_bucket"
        ]

        preprocessor = ColumnTransformer(
            transformers=[
                ("num", "passthrough", numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ]
        )

        self.pipeline = Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("model", HistGradientBoostingRegressor(
                    max_depth=4,
                    learning_rate=0.03,
                    max_iter=400,
                    min_samples_leaf=40,
                    random_state=42
                )),
            ]
        )

    def train_and_evaluate(self):
        self.build_pipeline()

        X_train, X_test, y_train, y_test = train_test_split(
            self.X,
            self.y,
            test_size=0.15,
            random_state=42
        )

        self.pipeline.fit(X_train, y_train)
        preds = self.pipeline.predict(X_test)

        # inverse transform to original scale
        y_test_orig = np.expm1(y_test)
        preds_orig = np.expm1(preds)

        mae = mean_absolute_error(y_test_orig, preds_orig)
        rmse = np.sqrt(mean_squared_error(y_test_orig, preds_orig))
        r2 = r2_score(y_test_orig, preds_orig)

        print(f"MAE:  {mae:.2f}")
        print(f"RMSE: {rmse:.2f}")
        print(f"R²:   {r2:.3f}")

    def save(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "pipeline": self.pipeline,
            "target": self.target
        }, path)
