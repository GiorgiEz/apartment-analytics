import pandas as pd

from datastorage.postgresql.PostgresDatabase import PostgresDatabase
from data_analysis.Preprocessing import Preprocessing

from data_analysis.EDA.MarketOverview import MarketOverview
from data_analysis.EDA.PriceAnalysis import PriceAnalysis
from data_analysis.EDA.ApartmentCharacteristics import ApartmentCharacteristics
from data_analysis.EDA.LocationInsights import LocationInsights



class RunEDA:
    """ Main class to Initialize all visualization objects and generate charts """
    def __init__(self):
        postgres_db = PostgresDatabase()

        sale_df = postgres_db.get_apartments_by_transaction('იყიდება')
        rent_df = postgres_db.get_apartments_by_transaction('ქირავდება თვიურად')

        # preprocess once
        sale_df = Preprocessing(sale_df).run()
        rent_df = Preprocessing(rent_df).run()

        combined_df = pd.concat([sale_df, rent_df])

        self.vis_objects = [
            MarketOverview(sale_df, rent_df, combined_df),
            PriceAnalysis(sale_df, rent_df, combined_df),
            ApartmentCharacteristics(sale_df, rent_df, combined_df),
            LocationInsights(sale_df, rent_df, combined_df)

        ]

    def main(self):
        for obj in self.vis_objects:
            obj.generate()
