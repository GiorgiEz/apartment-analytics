from scrape_clean_analyze.data_analysis.market_overview.CityDistributionPieChart import CityDistributionPieChart
from scrape_clean_analyze.data_analysis.market_overview.TransactionTypeDistributionBarChart import TransactionTypeDistributionBarChart
from scrape_clean_analyze.data_analysis.price_analysis.PriceDistributionHistogram import PriceDistributionHistogram
from scrape_clean_analyze.data_analysis.price_analysis.PricePerSqmBoxplot import PricePerSqmBoxplot
from scrape_clean_analyze.data_analysis.price_analysis.MedianPricePerCityBarChart import MedianPricePerCityBarChart


class RunEDA:
    """ Main class to Initialize all visualization objects and generate charts """
    def __init__(self, df, output_dir):
        self.vis_objects = [
            CityDistributionPieChart(df, output_dir), TransactionTypeDistributionBarChart(df, output_dir),
            PriceDistributionHistogram(df, output_dir), PricePerSqmBoxplot(df, output_dir),
            MedianPricePerCityBarChart(df, output_dir)
        ]

    def main(self):
        for obj in self.vis_objects:
            obj.generate()
