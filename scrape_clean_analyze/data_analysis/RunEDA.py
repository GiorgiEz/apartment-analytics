from .EDA.DistributionByCity import DistributionByCity
from .EDA.AveragePricePerSQM import AveragePricePerSQM
from .EDA.AveragePriceByCity import AveragePriceByCity
from .EDA.AveragePriceByArea import AveragePriceByArea


class RunEDA:
    def __init__(self):
        self.distribution_by_city = DistributionByCity()
        self.average_price_per_sqm = AveragePricePerSQM()
        self.average_price_by_city = AveragePriceByCity()
        self.average_price_by_area = AveragePriceByArea()

        self.transaction_types = ['იყიდება', 'ქირავდება დღიურად', 'ქირავდება თვიურად', 'გირავდება']
        self.cities = ['ქუთაისი', 'თბილისი', 'ბათუმი']

    def main(self):
        self.distribution_by_city.run()
        self.average_price_per_sqm.run()

        for city_name in self.cities:
            self.average_price_by_area.run(city_name)

        # Compare average apartment prices by cities for every transaction types
        for transaction_type in self.transaction_types:
            self.average_price_by_city.run(f'avg_price_by_city/{transaction_type}.png', transaction_type)

        # Compare average apartment prices in a specific city for every transaction types
        for city_name in self.cities:
            for transaction_type in self.transaction_types:
                self.average_price_by_city.run(f'avg_price_by_street/{city_name}/{transaction_type}.png',
                                               transaction_type, city_name)
