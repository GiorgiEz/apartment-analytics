from data_analysis.EDA.market_overview.CityDistributionPieChart import CityDistributionPieChart
from data_analysis.EDA.market_overview.TransactionTypeBarChart import TransactionTypeBarChart

from data_analysis.EDA.price_analysis.PriceDistributionHistogram import PriceDistributionHistogram
from data_analysis.EDA.price_analysis.PricePerSqmBoxplot import PricePerSqmBoxplot
from data_analysis.EDA.price_analysis.MedianPricePerCityBarChart import MedianPricePerCityBarChart

from data_analysis.EDA.apartment_characteristics.AreaDistributionHistogram import AreaDistributionHistogram
from data_analysis.EDA.apartment_characteristics.BedroomsVsPriceBoxplot import BedroomsVsPriceBoxplot
from data_analysis.EDA.apartment_characteristics.FloorDistributionBarChart import FloorDistributionBarChart

from data_analysis.EDA.location_insights.ListingsByDistrictBarChart import ListingsByDistrictBarChart
from data_analysis.EDA.location_insights.PricePerSqmByDistrictBoxplot import PricePerSqmByDistrictBoxplot

from data_analysis.EDA.time_analysis.ListingsOverTimeLineChart import ListingsOverTimeLineChart
from data_analysis.EDA.time_analysis.MedianPriceTrendOverTime import MedianPriceTrendOverTime



class RunEDA:
    """ Main class to Initialize all visualization objects and generate charts """
    def __init__(self):
        self.vis_objects = [
            CityDistributionPieChart(), TransactionTypeBarChart(),  # Market Overview

            PriceDistributionHistogram(), PricePerSqmBoxplot(),
            MedianPricePerCityBarChart(),  # Price Analysis

            AreaDistributionHistogram(), BedroomsVsPriceBoxplot(),
            FloorDistributionBarChart(),  # Apartment Characteristics

            ListingsByDistrictBarChart(),
            PricePerSqmByDistrictBoxplot(),  # Location Insights

            ListingsOverTimeLineChart(),
            MedianPriceTrendOverTime(),
        ]

    def main(self):
        for obj in self.vis_objects:
            obj.generate()
