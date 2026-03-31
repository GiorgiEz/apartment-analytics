from machine_learning.model_training.BaseModelTraining import BaseModelTraining
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor


class HistGradientBoostingTraining(BaseModelTraining):
    def __init__(self, train_df, validation_df, test_df):
        super().__init__(train_df, validation_df, test_df)
        self.name = "HistGradientBoostingRegressor"

    def build_model(self):
        # Column-wise preprocessing
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", "passthrough", self.numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), self.categorical_features),
            ]
        )

        # Full pipeline: preprocessing + tree-based regressor
        self.pipeline = Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("model", HistGradientBoostingRegressor(
                    max_depth=6,
                    learning_rate=0.08,
                    max_iter=400,
                    min_samples_leaf=40,
                    random_state=42
                )),
            ]
        )
