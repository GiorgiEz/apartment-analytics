from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from machine_learning.model_training.HistGradientBoostingTraining import HistGradientBoostingTraining
from machine_learning.model_training.LinearRegressionTraining import LinearRegressionTraining
from machine_learning.model_training.RandomForestTraining import RandomForestTraining
from machine_learning.model_training.DecisionTreeTraining import DecisionTreeTraining
from machine_learning.Preprocessing import Preprocessing
from datetime import timedelta
import pandas as pd



class ModelTrainingManager:
    def __init__(self):
        # Initialize database connection and load apartment datasets
        postgres_db = PostgresDatabase()

        # Load sale and rent apartment data separately
        self.sale_df = postgres_db.get_apartments_by_transaction('იყიდება')
        self.rent_df = postgres_db.get_apartments_by_transaction('ქირავდება თვიურად')

        # Train/test split ratio (85% train, 15% test)
        self.test_train_split_ratio = 0.85

    def time_split(self, df, min_test_samples=3000):
        """
        Prefer time-based split using last 14 days as test set.
        If test set is too small, fall back to 85/15 chronological split.
        """

        df = df.sort_values("upload_date").reset_index(drop=True)
        df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")

        # try last 14 days split
        cutoff_date = df["upload_date"].max() - timedelta(days=14)

        train = df[df["upload_date"] < cutoff_date].copy()
        test = df[df["upload_date"] >= cutoff_date].copy()

        # check if test set is large enough
        if len(test) < min_test_samples:
            split_index = int(len(df) * self.test_train_split_ratio)

            train = df.iloc[:split_index].copy()
            test = df.iloc[split_index:].copy()
            print("\n Using 85-15 time based train/test split \n")
        else:
            print("\n Using data from the past 14 days for test \n")

        return train, test

    def display_metrics(self, results_sale, results_rent):
        """ Display the metrics of sale, rent trained models_metadata as table """
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", None)
        pd.set_option("display.max_colwidth", None)

        sale_df = pd.DataFrame(results_sale).T
        rent_df = pd.DataFrame(results_rent).T

        print(f"\nSale Model Comparison\n {sale_df}")
        print(f"\nRent Model Comparison\n {rent_df}")

    def run(self):
        """Main ML pipeline: split → preprocess → train → evaluate → save"""

        # Split (85 - 15)
        sale_train, sale_test = self.time_split(self.sale_df)
        rent_train, rent_test = self.time_split(self.rent_df)

        # Preprocessing
        preprocessing = Preprocessing(sale_train=sale_train, rent_train=rent_train,
                                      sale_test=sale_test, rent_test=rent_test)
        preprocessing.run()

        sale_train = preprocessing.sale_train
        rent_train = preprocessing.rent_train
        sale_test = preprocessing.sale_test
        rent_test = preprocessing.rent_test

        # Train and save metrics for display
        results_sale = {}
        results_rent = {}

        sale_array = [
            HistGradientBoostingTraining(sale_train, sale_test),
            RandomForestTraining(sale_train, sale_test),
            DecisionTreeTraining(sale_train, sale_test),
            LinearRegressionTraining(sale_train, sale_test)
        ]

        rent_array = [
            HistGradientBoostingTraining(rent_train, rent_test),
            RandomForestTraining(rent_train, rent_test),
            DecisionTreeTraining(rent_train, rent_test),
            LinearRegressionTraining(rent_train, rent_test)
        ]

        for sale_regressor in sale_array:
            results_sale[sale_regressor.name] = sale_regressor.run()

        for rent_regressor in rent_array:
            results_rent[rent_regressor.name] = rent_regressor.run()

        # Displays MAE, RMSE and R2 metrics for all models_metadata
        self.display_metrics(results_sale, results_rent)
