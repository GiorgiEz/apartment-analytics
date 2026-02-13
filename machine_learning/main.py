from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from machine_learning.price_prediction_test.PriceModel import PriceModel
from Preprocessing import Preprocessing
from machine_learning.price_prediction_test.LocalPricePredictor import LocalPricePredictor
import numpy as np
from dotenv import load_dotenv
load_dotenv()



if __name__ == "__main__":
    "Step 1: Load the data from the database "
    postgres_db = PostgresDatabase()
    apartments_df = postgres_db.get_all_apartments()

    "Step 2: Prepare data for training "
    preprocessing = Preprocessing(apartments_df)
    preprocessing.run()
    apartments_df = preprocessing.apartments_df

    sale_df = apartments_df[apartments_df["transaction_type"] == "იყიდება"]
    rent_df = apartments_df[apartments_df["transaction_type"] == "ქირავდება თვიურად"]

    "Step 3: Train, evaluate and save ML models "
    print("\n=== SALE (price_per_sqm) ===")
    sale_model = PriceModel(sale_df, target="price_per_sqm")
    sale_model.train_and_evaluate()
    sale_model.save("models/sale_price_per_sqm.joblib")

    print("\n=== RENT (price) ===")
    rent_model = PriceModel(rent_df, target="price")
    rent_model.train_and_evaluate()
    rent_model.save("models/rent_price.joblib")

    "Step 4: Test models"
    sale_predictor = LocalPricePredictor("models/sale_price_per_sqm.joblib")
    rent_predictor = LocalPricePredictor("models/rent_price.joblib")

    city = "თბილისი"
    district = "ვაკე"
    area_m2 = 40
    bedrooms = 1
    floor = 3
    year = 1
    month = 2

    price_per_sqm = sale_predictor.predict_single(
        city=city,
        district=district,
        area_m2=area_m2,
        bedrooms=bedrooms,
        floor=floor,
        year=year,
        month=month
    )

    total_sale_price = price_per_sqm * area_m2

    monthly_rent = rent_predictor.predict_single(
        city=city,
        district=district,
        area_m2=area_m2,
        bedrooms=bedrooms,
        floor=floor,
        year=year,
        month=month
    )

    print(f"Sale price per sqm: {price_per_sqm:.2f}")
    print(f"Total sale price: {total_sale_price:.2f}")
    print(f"Monthly rent: {monthly_rent:.2f}")
