from ..data_analysis.EDA.market_overview.CityDistributionPieChart import CityDistributionPieChart
from ..data_analysis.EDA.market_overview.TransactionTypeBarChart import TransactionTypeBarChart

from ..data_analysis.EDA.price_analysis.PriceDistributionHistogram import PriceDistributionHistogram
from ..data_analysis.EDA.price_analysis.PricePerSqmBoxplot import PricePerSqmBoxplot
from ..data_analysis.EDA.price_analysis.MedianPricePerCityBarChart import MedianPricePerCityBarChart

from ..data_analysis.EDA.apartment_characteristics.AreaDistributionHistogram import AreaDistributionHistogram
from ..data_analysis.EDA.apartment_characteristics.BedroomsVsPriceBoxplot import BedroomsVsPriceBoxplot
from ..data_analysis.EDA.apartment_characteristics.FloorDistributionBarChart import FloorDistributionBarChart

from ..data_analysis.EDA.location_insights.ListingsByDistrictBarChart import ListingsByDistrictBarChart
from ..data_analysis.EDA.location_insights.PricePerSqmByDistrictBoxplot import PricePerSqmByDistrictBoxplot

from ..data_analysis.EDA.time_analysis.ListingsOverTimeLineChart import ListingsOverTimeLineChart
from ..data_analysis.EDA.time_analysis.MedianPriceTrendOverTime import MedianPriceTrendOverTime



class RunEDA:
    """ Main class to Initialize all visualization objects and generate charts """
    def __init__(self, df, output_dir):
        self.vis_objects = [
            CityDistributionPieChart(df, output_dir), TransactionTypeBarChart(df, output_dir),  # Market Overview

            PriceDistributionHistogram(df, output_dir), PricePerSqmBoxplot(df, output_dir),
            MedianPricePerCityBarChart(df, output_dir),  # Price Analysis

            AreaDistributionHistogram(df, output_dir), BedroomsVsPriceBoxplot(df, output_dir),
            FloorDistributionBarChart(df, output_dir),  # Apartment Characteristics

            ListingsByDistrictBarChart(df, output_dir),
            PricePerSqmByDistrictBoxplot(df, output_dir),  # Location Insights

            ListingsOverTimeLineChart(df, output_dir),
            MedianPriceTrendOverTime(df, output_dir),
        ]

    def main(self):
        for obj in self.vis_objects:
            obj.generate()
