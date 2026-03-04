from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from machine_learning.model_training.HistGradientBoostingTraining import HistGradientBoostingTraining
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

        print("\n=== FOR SALE APARTMENTS (price) - HistGradientBoosting ===")
        sale_model = HistGradientBoostingTraining(sale_train, sale_test)
        sale_model.run()
        sale_model.save("models/sale_prediction.joblib")

        print("\n=== MONTHLY RENT APARTMENTS (price) - HistGradientBoosting ===")
        rent_model = HistGradientBoostingTraining(rent_train, rent_test)
        rent_model.run()
        rent_model.save("models/rent_prediction.joblib")
