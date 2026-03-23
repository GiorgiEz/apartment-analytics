from abc import ABC, abstractmethod
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import numpy as np
import joblib
from pathlib import Path


class BaseModelTraining(ABC):
    def __init__(self, train_df, test_df):
        self.name = "BaseModel"
        self.train_df = train_df.copy()
        self.test_df = test_df.copy()

        self.target = "price"

        self.numeric_features = [
            "area_m2",
            "bedrooms",
            "floor",
            "upload_year",
            "upload_month",
            "district_median_price_per_sqm",
            "district_listing_count"
        ]

        self.categorical_features = [
            "city",
            "floor_bucket",
            "district_grouped",
            "area_bucket",
            "city_district"
        ]

        self.pipeline = None

        self._prepare_data()

    def _prepare_data(self):
        """Prepare X/y datasets and apply log transformation to target"""
        self.X_train = self.train_df.drop(columns=[self.target])
        self.y_train = np.log1p(self.train_df[self.target])

        self.X_test = self.test_df.drop(columns=[self.target])
        self.y_test = np.log1p(self.test_df[self.target])

    @abstractmethod
    def build_model(self):
        """Child classes must implement this method"""
        pass

    def train(self):
        """Train the model pipeline"""
        self.build_model()
        self.pipeline.fit(self.X_train, self.y_train)

    def evaluate(self):
        """Evaluate model performance on the test dataset"""
        preds = self.pipeline.predict(self.X_test)

        y_test_orig = np.expm1(self.y_test)
        preds_orig = np.expm1(preds)

        mae = f'{round(mean_absolute_error(y_test_orig, preds_orig), 2)} $'
        mape = f'{round(mean_absolute_percentage_error(y_test_orig, preds_orig) * 100, 2)} %'
        rmse = f'{round(np.sqrt(mean_squared_error(y_test_orig, preds_orig)), 2)} $'
        r2 = round(r2_score(y_test_orig, preds_orig), 2)

        return {
            "MAE": mae,
            "MAPE(%)": mape,
            "RMSE": rmse,
            "R2": r2,
            "Train samples": len(self.X_train),
            "Test samples": len(self.X_test)
        }

    def save(self, path):
        """Save trained model pipeline"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, path)

    def run(self):
        """Full training pipeline: train → evaluate"""
        self.train()
        return self.evaluate()
