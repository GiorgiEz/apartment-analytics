from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from machine_learning.PriceModel import PriceModel
from Preprocessing import Preprocessing
import pandas as pd
import numpy as np

from dotenv import load_dotenv
load_dotenv()



if __name__ == "__main__":
    postgres_db = PostgresDatabase()
    apartments_df = postgres_db.get_all_apartments()

    preprocessing = Preprocessing(apartments_df)
    preprocessing.run()
    apartments_df = preprocessing.apartments_df

    sale_df = apartments_df[apartments_df["transaction_type"] == "იყიდება"]
    rent_df = apartments_df[apartments_df["transaction_type"] == "ქირავდება თვიურად"]

    sale_model = PriceModel(sale_df, target="price_per_sqm")
    sale_model.train_and_evaluate()

    rent_model = PriceModel(rent_df, target="price")
    rent_model.train_and_evaluate()
