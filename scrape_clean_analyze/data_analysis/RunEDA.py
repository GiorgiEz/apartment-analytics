from .EDA.CityDistributionPieChart import CityDistributionPieChart


class RunEDA:
    def __init__(self, df, output_dir):
        self.distribution_by_city = CityDistributionPieChart(df, output_dir)

    def main(self):
        self.distribution_by_city.generate()
