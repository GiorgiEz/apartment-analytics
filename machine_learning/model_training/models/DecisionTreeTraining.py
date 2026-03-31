from machine_learning.model_training.BaseModelTraining import BaseModelTraining
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor


class DecisionTreeTraining(BaseModelTraining):
    def __init__(self, train_df, validation_df, test_df):
        super().__init__(train_df, validation_df, test_df)
        self.name = "DecisionTreeRegressor"

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
                ("model", DecisionTreeRegressor(
                    max_depth=25,
                    min_samples_leaf=10,
                    random_state=42
                )),
            ]
        )