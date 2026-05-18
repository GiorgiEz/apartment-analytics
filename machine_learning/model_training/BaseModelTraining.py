from abc import ABC, abstractmethod
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
import numpy as np
import pandas as pd
import os, joblib
from sklearn.model_selection import cross_val_score



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
            # "district_name"
            "floor_bucket",
            "district_grouped",
            "area_bucket",
            "city_district"
        ]

        self.pipeline = None

        self._prepare_data()

    @abstractmethod
    def build_model(self):
        """Child classes must implement this method"""
        pass

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

        train_preds = self.pipeline.predict(self.X_train)

        return {
            "MAE": f'{round(mean_absolute_error(y_test_orig, preds_orig), 2)} $',
            "MAPE(%)": f'{round(mean_absolute_percentage_error(y_test_orig, preds_orig) * 100, 2)} %',
            "RMSE": f'{round(np.sqrt(mean_squared_error(y_test_orig, preds_orig)), 2)} $',
            "R2 Test": f'{int(round(r2_score(y_test_orig, preds_orig) * 100, 0))} %',
            "R2 Train": f'{int(round(r2_score(np.expm1(self.y_train), np.expm1(train_preds)) * 100, 0))} %',
            "Train samples": len(self.X_train) + len(self.X_val),
            "Test samples": len(self.X_test)
        }

    def __print_feature_importance(self):
        """ Print aggregated feature importances """

        model = self.pipeline.named_steps["model"]
        preprocessor = self.pipeline.named_steps["preprocess"]

        feature_names = preprocessor.get_feature_names_out()
        importances = model.feature_importances_

        importance_df = pd.DataFrame({"feature": feature_names, "importance": importances})

        grouped_importance = {}

        for _, row in importance_df.iterrows():
            feature = row["feature"]
            importance = row["importance"]

            # Numerical features
            if feature.startswith("num__"):
                original_feature = feature.replace("num__", "")

            # Categorical features
            elif feature.startswith("cat__"):
                feature_part = feature.replace("cat__", "")

                # Example: city_Tbilisi -> city. district_grouped_Vake -> district_grouped

                original_feature = feature_part.split("_")[0]

                # Handle special names manually
                if feature_part.startswith("district_grouped"):
                    original_feature = "district_grouped"

                elif feature_part.startswith("city_district"):
                    original_feature = "city_district"

                elif feature_part.startswith("floor_bucket"):
                    original_feature = "floor_bucket"

                elif feature_part.startswith("area_bucket"):
                    original_feature = "area_bucket"

            else:
                original_feature = feature

            grouped_importance[original_feature] = (grouped_importance.get(original_feature, 0) + importance)

        grouped_df = pd.DataFrame({
            "feature": grouped_importance.keys(),
            "importance": [round(value * 100, 2) for value in grouped_importance.values()]
        })

        grouped_df = grouped_df.sort_values(by="importance", ascending=False)

        print("\nGrouped Feature Importances:\n")
        print(grouped_df.to_string(index=False))

        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6))

        plt.barh(grouped_df["feature"], grouped_df["importance"])

        plt.xlabel("Importance")
        plt.ylabel("Feature")

        plt.gca().invert_yaxis()

        plt.tight_layout()
        plt.show()

    def save(self, base_dir, transaction_type):
        """Save trained RandomForest pipeline with transaction type in filename"""
        if self.pipeline is None:
            raise ValueError("Pipeline is not trained.")

        if self.name != "RandomForestRegressor":
            return

        os.makedirs(base_dir, exist_ok=True)  # Create directory if not exists

        filename = f"{self.name}_{transaction_type}.joblib"  # Build filename
        filepath = os.path.join(base_dir, filename)

        joblib.dump(self.pipeline, filepath)  # Save

        print(f"Model saved to: {filepath}")

    def run(self):
        """Full training pipeline: train → evaluate"""
        self.train()
        # self.__print_feature_importance()
        return self.evaluate()
