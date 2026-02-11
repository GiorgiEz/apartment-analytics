from scrape_clean_analyze.data_analysis.market_overview.CityDistributionPieChart import CityDistributionPieChart
from scrape_clean_analyze.data_analysis.market_overview.TransactionTypeDistributionBarChart import (TransactionTypeDistributionBarChart)


class RunEDA:
    def __init__(self, df, output_dir):
        self.distribution_by_city = CityDistributionPieChart(df, output_dir)
        self.transaction_type_distribution = TransactionTypeDistributionBarChart(df, output_dir)

    def main(self):
        self.distribution_by_city.generate()
        self.transaction_type_distribution.generate()
