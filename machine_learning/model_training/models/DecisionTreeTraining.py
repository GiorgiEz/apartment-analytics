from machine_learning.model_training.BaseModelTraining import BaseModelTraining
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score
from machine_learning.pipeline.FeatureEngineeringTransformer import FeatureEngineeringTransformer



class DecisionTreeTraining(BaseModelTraining):
    def __init__(self, train_df, validation_df, test_df):
        super().__init__(train_df, validation_df, test_df)
        self.name = "DecisionTreeRegressor"

        self.best_params = {
            "max_depth": 10,
            "min_samples_leaf": 5,
            "min_samples_split": 25,
            "max_leaf_nodes": 200,
        }

    def tune_hyperparameters(self):
        best_score = -1
        best_params = None

        param_grid = {
            "max_depth": [3, 5, 7, 10, 12, 15, 20, None],
            "min_samples_leaf": [1, 2, 5, 10, 20, 50],
            "min_samples_split": [2, 5, 10, 20, 50],
            "max_leaf_nodes": [20, 50, 100, 200, 500, None],
        }

        for depth in param_grid["max_depth"]:
            for leaf in param_grid["min_samples_leaf"]:
                for split in param_grid["min_samples_split"]:
                    for max_nodes in param_grid["max_leaf_nodes"]:

                        # skip invalid combinations
                        if split < 2 * leaf:
                            continue

                        self.pipeline = Pipeline(
                            steps=[
                                ("feature_engineering", FeatureEngineeringTransformer()),
                                ("preprocess", self.build_preprocessor()),
                                ("model", DecisionTreeRegressor(
                                    max_depth=depth,
                                    min_samples_leaf=leaf,
                                    min_samples_split=split,
                                    max_leaf_nodes=max_nodes,
                                    random_state=42
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
                                "max_depth": depth,
                                "min_samples_leaf": leaf,
                                "min_samples_split": split,
                                "max_leaf_nodes": max_nodes,
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
                ("model", DecisionTreeRegressor(
                    **self.best_params,
                    random_state=42
                )),
            ]
        )
