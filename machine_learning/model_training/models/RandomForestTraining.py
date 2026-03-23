from machine_learning.model_training.BaseModelTraining import BaseModelTraining
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor


class RandomForestTraining(BaseModelTraining):
    def __init__(self, train_df, test_df):
        super().__init__(train_df, test_df)
        self.name = "RandomForestRegressor"

    def build_model(self):
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", "passthrough", self.numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), self.categorical_features),
            ]
        )

        self.pipeline = Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("model", RandomForestRegressor(
                    n_estimators=400,
                    max_depth=25,
                    min_samples_leaf=4,
                    random_state=42,
                    n_jobs=-1
                )),
            ]
        )