from machine_learning.model_training.BaseModelTraining import BaseModelTraining
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score
from backend.machine_learning.pipeline.FeatureEngineeringTransformer import FeatureEngineeringTransformer



class HistGradientBoostingTraining(BaseModelTraining):
    def __init__(self, train_df, validation_df, test_df):
        super().__init__(train_df, validation_df, test_df)
        self.name = "HistGradientBoostingRegressor"

        self.best_params = {
            "max_iter": 500,
            "learning_rate": 0.1,
            "max_depth": 12,
            "min_samples_leaf": 10,
            "l2_regularization": 0.1,
            "random_state": 42,
        }

    def tune_hyperparameters(self):
        best_score = -1
        best_params = None

        param_grid = {
            "max_iter": [300, 350],
            "learning_rate": [0.15, 0.2],
            "max_depth": [10, 15],
            "min_samples_leaf": [10, 12],
            "l2_regularization": [0.1, 0.2],
        }

        for itr in param_grid["max_iter"]:
            for rate in param_grid["learning_rate"]:
                for depth in param_grid["max_depth"]:
                    for leaf in param_grid["min_samples_leaf"]:
                        for l2 in param_grid["l2_regularization"]:

                            # build model with params
                            self.pipeline = Pipeline(
                                steps=[
                                    ("feature_engineering", FeatureEngineeringTransformer()),
                                    ("preprocess", self.build_preprocessor()),
                                    ("model", HistGradientBoostingRegressor(
                                        max_iter=itr,
                                        learning_rate=rate,
                                        max_depth=depth,
                                        min_samples_leaf=leaf,
                                        l2_regularization=l2,
                                        random_state=42,
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
                                    "max_iter": itr,
                                    "learning_rate": rate,
                                    "max_depth": depth,
                                    "min_samples_leaf": leaf,
                                    "l2_regularization": l2,
                                }

        print("Best params:", best_params)
        print("Best validation R2:", best_score)

        self.best_params = best_params

    def build_model(self):
        # Used for parameter tuning. Could take a couple of minutes depending on amount of combinations testing
        # self.tune_hyperparameters()

        self.pipeline = Pipeline(
            steps=[
                ("feature_engineering", FeatureEngineeringTransformer()),
                ("preprocess", self.build_preprocessor()),
                ("model", HistGradientBoostingRegressor(**self.best_params)),
            ]
        )
