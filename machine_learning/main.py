from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from machine_learning.price_prediction_test.PriceModel import PriceModel
from Preprocessing import Preprocessing
from machine_learning.price_prediction_test.LocalPricePredictor import LocalPricePredictor



if __name__ == "__main__":
    "Step 1: Load the data from the database"
    def time_split(df, ratio=0.85):
        df = df.sort_values("upload_date").reset_index(drop=True)
        split_index = int(len(df) * ratio)

        train = df.iloc[:split_index].copy()
        test = df.iloc[split_index:].copy()

        return train, test

    postgres_db = PostgresDatabase()
    sale_df = postgres_db.get_apartments_by_transaction('იყიდება')
    rent_df = postgres_db.get_apartments_by_transaction('ქირავდება თვიურად')

    sale_train, sale_test = time_split(sale_df)
    rent_train, rent_test = time_split(rent_df)

    "Step 2: Prepare data for training"
    preprocessing = Preprocessing(sale_train=sale_train, rent_train=rent_train, sale_test=sale_test, rent_test=rent_test)
    preprocessing.run()

    sale_train = preprocessing.sale_train
    rent_train = preprocessing.rent_train
    sale_test = preprocessing.sale_test
    rent_test = preprocessing.rent_test

    "Step 3: Train, evaluate and save ML models"
    print("\n=== FOR SALE APARTMENTS (price) ===")
    sale_model = PriceModel(sale_train, sale_test)
    sale_model.train_and_evaluate()
    sale_model.save("models/sale_prediction.joblib")

    print("\n=== MONTHLY RENT APARTMENTS (price) ===")
    rent_model = PriceModel(rent_train, rent_test)
    rent_model.train_and_evaluate()
    rent_model.save("models/rent_prediction.joblib")

    "Step 4: Test models"
    predictor = LocalPricePredictor()

    city = "თბილისი"
    district = "ვაკე"
    area_m2 = 40
    bedrooms = 1
    floor = 3
    year = 1
    month = 2

    prices = predictor.predict_single(
        city=city,
        district=district,
        area_m2=area_m2,
        bedrooms=bedrooms,
        floor=floor,
        year=year,
        month=month
    )

    print(f"\nTotal sale price: {prices['sale_price']}")
    print(f"Monthly rent: {prices['rent_price']}")
