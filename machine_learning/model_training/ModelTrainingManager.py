from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from machine_learning.model_training.HistGradientBoostingTraining import HistGradientBoostingTraining
from machine_learning.model_training.LinearRegressionTraining import LinearRegressionTraining
from machine_learning.model_training.RandomForestTraining import RandomForestTraining
from machine_learning.model_training.DecisionTreeTraining import DecisionTreeTraining
from machine_learning.Preprocessing import Preprocessing



class ModelTrainingManager:
    def __init__(self):
        # Initialize database connection and load apartment datasets
        postgres_db = PostgresDatabase()

        # Load sale and rent apartment data separately
        self.sale_df = postgres_db.get_apartments_by_transaction('იყიდება')
        self.rent_df = postgres_db.get_apartments_by_transaction('ქირავდება თვიურად')

        # Train/test split ratio (85% train, 15% test)
        self.test_train_split_ration = 0.85

    def time_split(self, df):
        """Split dataset into train and test sets based on upload_date"""

        df = df.sort_values("upload_date").reset_index(drop=True)
        split_index = int(len(df) * self.test_train_split_ration)

        train = df.iloc[:split_index].copy()
        test = df.iloc[split_index:].copy()

        return train, test

    def run(self):
        """Main ML pipeline: split → preprocess → train → evaluate → save"""

        sale_train, sale_test = self.time_split(self.sale_df)
        rent_train, rent_test = self.time_split(self.rent_df)

        preprocessing = Preprocessing(sale_train=sale_train, rent_train=rent_train,
                                      sale_test=sale_test, rent_test=rent_test)
        preprocessing.run()

        sale_train = preprocessing.sale_train
        rent_train = preprocessing.rent_train
        sale_test = preprocessing.sale_test
        rent_test = preprocessing.rent_test

        # HistGradientBoosting
        print("\n=== FOR SALE APARTMENTS (price) - HistGradientBoosting ===")
        sale_hist_gradient_boosting = HistGradientBoostingTraining(sale_train, sale_test)
        sale_hist_gradient_boosting.run()
        sale_hist_gradient_boosting.save("models/sale_prediction.joblib")

        print("\n=== MONTHLY RENT APARTMENTS (price) - HistGradientBoosting ===")
        rent_hist_gradient_boosting = HistGradientBoostingTraining(rent_train, rent_test)
        rent_hist_gradient_boosting.run()
        rent_hist_gradient_boosting.save("models/rent_prediction.joblib")

        # LinearRegression
        print("\n=== FOR SALE APARTMENTS (price) - LinearRegression ===")
        sale_linear_regression = LinearRegressionTraining(sale_train, sale_test)
        sale_linear_regression.run()

        print("\n=== MONTHLY RENT APARTMENTS (price) - LinearRegression ===")
        rent_linear_regression = LinearRegressionTraining(rent_train, rent_test)
        rent_linear_regression.run()

        # RandomForestRegression
        print("\n=== FOR SALE APARTMENTS (price) - RandomForestRegression ===")
        sale_random_forest_regression = RandomForestTraining(sale_train, sale_test)
        sale_random_forest_regression.run()

        print("\n=== MONTHLY RENT APARTMENTS (price) - RandomForestRegression ===")
        rent_random_forest_regression = RandomForestTraining(rent_train, rent_test)
        rent_random_forest_regression.run()

        # DecisionTreeRegression
        print("\n=== FOR SALE APARTMENTS (price) - DecisionTreeRegression ===")
        sale_decision_tree_regression = DecisionTreeTraining(sale_train, sale_test)
        sale_decision_tree_regression.run()

        print("\n=== MONTHLY RENT APARTMENTS (price) - DecisionTreeRegression ===")
        rent_decision_tree_regression = DecisionTreeTraining(rent_train, rent_test)
        rent_decision_tree_regression.run()
