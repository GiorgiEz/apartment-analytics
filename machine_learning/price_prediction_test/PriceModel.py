from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from pathlib import Path
import numpy as np


class PriceModel:
    """Trains and evaluates a price or price_per_sqm regression model"""

    def __init__(self, train_df, test_df):
        self.train_df = train_df.copy()
        self.test_df = test_df.copy()
        self.target = 'price'

        self._prepare_data()

    def _prepare_data(self):
        """Prepare train and test data for modeling"""
        # Remove rows with missing target
        self.train_df = self.train_df.dropna(subset=[self.target])
        self.test_df = self.test_df.dropna(subset=[self.target])

        # Sort by time (safety)
        self.train_df = self.train_df.sort_values(["upload_year", "upload_month"]).reset_index(drop=True)
        self.test_df = self.test_df.sort_values(["upload_year", "upload_month"]).reset_index(drop=True)

        # Targets
        self.y_train = np.log1p(self.train_df[self.target])
        self.y_test = np.log1p(self.test_df[self.target])

        # Features
        self.X_train = self.train_df.drop(columns=[self.target])
        self.X_test = self.test_df.drop(columns=[self.target])

    def build_pipeline(self):
        numeric_features = [
            "area_m2",
            "bedrooms",
            "floor",
            "upload_year",
            "upload_month"
        ]

        categorical_features = [
            "city",
            "district_name"
        ]

        # Column-wise preprocessing
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", "passthrough", numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical_features),
            ]
        )

        # Full pipeline: preprocessing + tree-based regressor
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
        """Train model and evaluate on test set"""

        self.build_pipeline()

        # Train model
        self.pipeline.fit(self.X_train, self.y_train)

        # Predict (log space)
        preds = self.pipeline.predict(self.X_test)

        # Convert back to original scale
        y_test_orig = np.expm1(self.y_test)
        preds_orig = np.expm1(preds)

        # Metrics
        mae = mean_absolute_error(y_test_orig, preds_orig)
        rmse = np.sqrt(mean_squared_error(y_test_orig, preds_orig))
        r2 = r2_score(y_test_orig, preds_orig)

        print("Evaluation (time-based split)")
        print(f"Train samples: {len(self.X_train)}")
        print(f"Test samples:  {len(self.X_test)}")
        print(f"MAE:  {mae:.2f}")
        print(f"RMSE: {rmse:.2f}")
        print(f"R²:   {r2:.3f}")

    def save(self, path):
        # Persist trained pipeline and metadata
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"pipeline": self.pipeline, "target": self.target}, path)
