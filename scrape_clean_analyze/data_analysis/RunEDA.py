from scrape_clean_analyze.data_analysis.market_overview.CityDistributionPieChart import CityDistributionPieChart
from scrape_clean_analyze.data_analysis.market_overview.TransactionTypeDistributionBarChart import TransactionTypeDistributionBarChart
from scrape_clean_analyze.data_analysis.price_analysis.PriceDistributionHistogram import PriceDistributionHistogram
from scrape_clean_analyze.data_analysis.price_analysis.PricePerSqmBoxplot import PricePerSqmBoxplot
from scrape_clean_analyze.data_analysis.price_analysis.MedianPricePerCityBarChart import MedianPricePerCityBarChart


class RunEDA:
    def __init__(self, df, output_dir):
        self.distribution_by_city = CityDistributionPieChart(df, output_dir)
        self.transaction_type_distribution = TransactionTypeDistributionBarChart(df, output_dir)
        self.price_distribution_sale_rent = PriceDistributionHistogram(df, output_dir)
        self.price_per_sqm = PricePerSqmBoxplot(df, output_dir)
        self.median_price_per_city = MedianPricePerCityBarChart(df, output_dir)

    def main(self):
        self.distribution_by_city.generate()
        self.transaction_type_distribution.generate()
        self.price_distribution_sale_rent.generate()
        self.price_per_sqm.generate()
        self.median_price_per_city.generate()
