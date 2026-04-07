from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from machine_learning.model_training.models.HistGradientBoostingTraining import HistGradientBoostingTraining
from machine_learning.model_training.models.LinearRegressionTraining import LinearRegressionTraining
from machine_learning.model_training.models.RandomForestTraining import RandomForestTraining
from machine_learning.model_training.models.DecisionTreeTraining import DecisionTreeTraining
from machine_learning.pipeline.Preprocessing import Preprocessing
from machine_learning.pipeline.InferenceLimits import InferenceLimits
from config import paths
import pandas as pd



class ModelTrainingManager:
    def __init__(self):
        postgres_db = PostgresDatabase()  # Initialize database connection and load apartment datasets

        # Load sale and rent apartment data separately
        self.sale_df = postgres_db.get_apartments_by_transaction('იყიდება')
        self.rent_df = postgres_db.get_apartments_by_transaction('ქირავდება თვიურად')

    def __time_split(self, df):
        """Split dataset into train, validation and test sets based on upload_date (70-15-15)"""
        df = df.sort_values("upload_date").reset_index(drop=True)

        n = len(df)

        train = df.iloc[:int(0.7 * n)].copy()
        validation = df.iloc[int(0.7 * n):int(0.85 * n)].copy()
        test = df.iloc[int(0.85 * n):].copy()

        return train, validation, test

    def __deduplicate(self):
        self.__display_df_length({"Sale": self.sale_df, "Rent": self.rent_df})
        print("DEDUPLICATION -->")
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
        self.__display_df_length({"Sale": self.sale_df, "Rent": self.rent_df})

    def __display_df_length(self, type_df_map):
        for transaction_type, df in type_df_map.items():
            print(f"{transaction_type} Dataframe Length: {len(df)}")

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

        """ 1. Split (70 - 15 - 15) into train, validation and test sets """
        sale_train, sale_validation, sale_test = self.__time_split(self.sale_df)
        rent_train, rent_validation, rent_test = self.__time_split(self.rent_df)

        """ 2. Preprocessing """
        print("PREPROCESSING -->")
        sale_preprocessing = Preprocessing(train_df=sale_train, validation_df=sale_validation,
                                           test_df=sale_test, transaction_type="Sale")
        sale_preprocessing.run()
        sale_train, sale_validation, sale_test = sale_preprocessing.get_dataframes()

        rent_preprocessing = Preprocessing(train_df=rent_train, validation_df=rent_validation,
                                           test_df=rent_test, transaction_type="Rent")
        rent_preprocessing.run()
        rent_train, rent_validation, rent_test = rent_preprocessing.get_dataframes()

        self.__display_df_length({"Sale": pd.concat([sale_train, sale_validation, sale_test]),
                                  "Rent": pd.concat([rent_train, rent_validation, rent_test])})

        """ 3. Save inference Limit schema """
        InferenceLimits(sale_train, sale_validation, "Sale", paths.BACKEND_INFERENCE_SCHEMA_DIR).run()
        InferenceLimits(rent_train, rent_validation, "Rent", paths.BACKEND_INFERENCE_SCHEMA_DIR).run()

        """ 4. Train and save metrics for display """
        results_sale, results_rent = {}, {}

        sale_array = [
            HistGradientBoostingTraining(sale_train, sale_validation, sale_test),
            RandomForestTraining(sale_train, sale_validation, sale_test),
            DecisionTreeTraining(sale_train, sale_validation, sale_test),
            LinearRegressionTraining(sale_train, sale_validation, sale_test)
        ]

        rent_array = [
            HistGradientBoostingTraining(rent_train, rent_validation, rent_test),
            RandomForestTraining(rent_train, rent_validation, rent_test),
            DecisionTreeTraining(rent_train, rent_validation, rent_test),
            LinearRegressionTraining(rent_train, rent_validation, rent_test)
        ]

        for sale_regressor in sale_array:
            results_sale[sale_regressor.name] = sale_regressor.run()
            sale_regressor.save(base_dir=paths.BACKEND_ML_TRAINED_MODELS_DIR, transaction_type="Sale")

        for rent_regressor in rent_array:
            results_rent[rent_regressor.name] = rent_regressor.run()
            rent_regressor.save(base_dir=paths.BACKEND_ML_TRAINED_MODELS_DIR, transaction_type="Rent")

        """ 5. Displays MAE, MAPE, RMSE and R2 metrics for all models_metadata """
        self.__display_metrics(results_sale, results_rent)
