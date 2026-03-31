from machine_learning.model_training.BaseModelTraining import BaseModelTraining
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score


class RandomForestTraining(BaseModelTraining):
    def __init__(self, train_df, validation_df, test_df, transaction_type):
        super().__init__(train_df, validation_df, test_df)
        self.name = "RandomForestRegressor"
        self.best_params = None
        self.transaction_type = transaction_type

        self.best_params_sale = {
            "n_estimators": 450,
            "max_depth": 30,
            "min_samples_leaf": 2,
            "max_features": 0.5,
            "min_samples_split": 7,
        }

        self.best_params_rent = {
            "n_estimators": 450,
            "max_depth": 25,
            "min_samples_leaf": 2,
            "max_features": "sqrt",
            "min_samples_split": 2,
        }

    def build_preprocessor(self):
        return ColumnTransformer(
            transformers=[
                ("num", "passthrough", self.numeric_features),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), self.categorical_features),
            ]
        )

    def tune_hyperparameters(self):
        best_score = -1
        best_params = None

        param_grid = {
            "n_estimators": [400, 450, 500],
            "max_depth": [30, 25, 35],
            "min_samples_leaf": [2, 3],
            "max_features": ["sqrt", 0.7],
            "min_samples_split": [2, 3, 8],
        }

        for n in param_grid["n_estimators"]:
            for depth in param_grid["max_depth"]:
                for leaf in param_grid["min_samples_leaf"]:
                    for feature in param_grid["max_features"]:
                        for split in param_grid["min_samples_split"]:

                            # build model with params
                            self.pipeline = Pipeline(
                                steps=[
                                    ("preprocess", self.build_preprocessor()),
                                    ("model", RandomForestRegressor(
                                        n_estimators=n,
                                        max_depth=depth,
                                        min_samples_leaf=leaf,
                                        max_features=feature,
                                        min_samples_split=split,
                                        random_state=42,
                                        n_jobs=-1
                                    )),
                                ]
                            )

                            # train
                            self.pipeline.fit(self.X_train, self.y_train)

                            # validate
                            preds = self.pipeline.predict(self.X_val)
                            score = r2_score(self.y_val, preds)

                            if score > best_score:
                                best_score = score
                                best_params = {
                                    "n_estimators": n,
                                    "max_depth": depth,
                                    "min_samples_leaf": leaf,
                                    "max_features": feature,
                                    "min_samples_split": split,
                                }

        print("Best params:", best_params)
        print("Best validation R2:", best_score)

        self.best_params = best_params

    def build_model(self):
        # if self.best_params is None:
        #     self.tune_hyperparameters()

        self.pipeline = Pipeline(
            steps=[
                ("preprocess", self.build_preprocessor()),
                ("model", RandomForestRegressor(
                    **self.best_params_sale if self.transaction_type == "sale" else self.best_params_rent,
                    random_state=42,
                    n_jobs=-1
                )),
            ]
        )