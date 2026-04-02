from abc import ABC, abstractmethod
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import numpy as np
import pandas as pd



class BaseModelTraining(ABC):
    def __init__(self, train_df, validation_df, test_df):
        self.name = "BaseModel"
        self.train_df = train_df.copy()
        self.validation_df = validation_df.copy()
        self.test_df = test_df.copy()

        self.target = "price"

        self.numeric_features = [
            "area_m2",
            "bedrooms",
            "floor",
            "upload_year",
            "upload_month",
            "district_median_price_per_sqm",
            "district_listing_count",
            "area_per_bedroom",
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

    def build_preprocessor(self):
        return ColumnTransformer(
            transformers=[
                ("num", "passthrough", self.numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), self.categorical_features),
            ]
        )

    def _prepare_data(self):
        """Prepare X/y datasets and apply log transformation to target"""
        self.X_train = self.train_df.drop(columns=[self.target])
        self.y_train = np.log1p(self.train_df[self.target])

        self.X_val = self.validation_df.drop(columns=[self.target])
        self.y_val = np.log1p(self.validation_df[self.target])

        self.X_test = self.test_df.drop(columns=[self.target])
        self.y_test = np.log1p(self.test_df[self.target])

    @abstractmethod
    def build_model(self):
        """Child classes must implement this method"""
        pass

    def train(self):
        """Train the model pipeline"""
        self.build_model()

        # After tuning is done we can combine validation df with training df and use them for training
        X_full = pd.concat([self.X_train, self.X_val])
        y_full = pd.concat([self.y_train, self.y_val])

        self.pipeline.fit(X_full, y_full)

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
            "Train samples": len(self.X_train) + len(self.X_val),
            "Test samples": len(self.X_test)
        }

    def run(self):
        """Full training pipeline: train → evaluate"""
        self.train()
        return self.evaluate()
