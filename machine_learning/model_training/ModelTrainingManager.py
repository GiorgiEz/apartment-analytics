from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from machine_learning.model_training.models.HistGradientBoostingTraining import HistGradientBoostingTraining
from machine_learning.model_training.models.LinearRegressionTraining import LinearRegressionTraining
from machine_learning.model_training.models.RandomForestTraining import RandomForestTraining
from machine_learning.model_training.models.DecisionTreeTraining import DecisionTreeTraining
from machine_learning.pipeline.FeatureEngineering import FeatureEngineering
from machine_learning.pipeline.Preprocessing import Preprocessing
import pandas as pd



class ModelTrainingManager:
    def __init__(self):
        postgres_db = PostgresDatabase()  # Initialize database connection and load apartment datasets

        # Load sale and rent apartment data separately
        self.sale_df = postgres_db.get_apartments_by_transaction('იყიდება')
        self.rent_df = postgres_db.get_apartments_by_transaction('ქირავდება თვიურად')

        self.test_train_split_ratio = 0.85  # Train/test split ratio (85% train, 15% test)

    def __time_split(self, df):
        """Split dataset into train and test sets based on upload_date"""
        df = df.sort_values("upload_date").reset_index(drop=True)
        split_index = int(len(df) * self.test_train_split_ratio)

        return df.iloc[:split_index].copy(), df.iloc[split_index:].copy()

    def __deduplicate(self):
        self.sale_df = (
            self.sale_df.sort_values("upload_date")
            .drop_duplicates(
                subset=["price", "area_m2", "city", "district_name", "street_address", "floor", "bedrooms"],
                keep="last"
            )
        )
        self.rent_df = (
            self.rent_df.sort_values("upload_date")
            .drop_duplicates(
                subset=["price", "area_m2", "city", "district_name", "street_address", "floor", "bedrooms"],
                keep="last"
            )
        )

    def __display_metrics(self, results_sale, results_rent):
        """ Display the metrics of sale, rent trained models_metadata as table """
        pd.set_option("display.max_rows", None)
        pd.set_option("display.max_columns", None)
        pd.set_option("display.width", None)
        pd.set_option("display.max_colwidth", None)
        print(f"\nSale Model Comparison\n {pd.DataFrame(results_sale).T}")
        print(f"\nRent Model Comparison\n {pd.DataFrame(results_rent).T}")

    def run(self):
        """Main ML pipeline: split → preprocess → train → evaluate → save"""
        self.__deduplicate()  # Remove duplicates before split

        # Split (85 - 15)
        sale_train, sale_test = self.__time_split(self.sale_df)
        rent_train, rent_test = self.__time_split(self.rent_df)

        # Preprocessing
        preprocessing = Preprocessing(sale_train=sale_train, rent_train=rent_train,
                                      sale_test=sale_test, rent_test=rent_test)
        preprocessing.run()
        sale_train, sale_test, rent_train, rent_test = preprocessing.get_dfs()

        # Feature Engineering
        feature_engineering = FeatureEngineering(sale_train=sale_train, rent_train=rent_train,
                                                 sale_test=sale_test, rent_test=rent_test)

        feature_engineering.run()
        sale_train, sale_test, rent_train, rent_test = feature_engineering.get_dfs()

        # Train and save metrics for display
        results_sale, results_rent = {}, {}

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
        self.__display_metrics(results_sale, results_rent)
