from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
from scrape_clean_analyze.utils.geo_to_eng_mappings import CITY_MAP, TRANSACTION_TYPE_MAP
import matplotlib.pyplot as plt
import numpy as np


class MedianPricePerCityBarChart(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.base_path = "price_analysis/median_bar_charts/median_price_"

    def _generate_for_type(self, geo_transaction_type):
        """
        Generates bar charts of median apartment prices by city, separately for
        Sale and Monthly Rent listings. Provides a clear, executive-level comparison of
        typical pricing across markets.
        """

        # Filter relevant data
        df_filtered = self.df[
            (self.df["transaction_type"] == geo_transaction_type)
            & (self.df["price"] > 0)
            & (self.df["city"].notna())
        ].copy()

        if df_filtered.empty:
            return

        english_type = TRANSACTION_TYPE_MAP.get(geo_transaction_type)

        medians = {}
        for city in df_filtered["city"].unique():
            city_prices = df_filtered[df_filtered["city"] == city]["price"].values

            if len(city_prices) < 10:
                continue

            medians[city] = np.median(city_prices)

        if not medians:
            return

        # Sort cities by median
        sorted_items = sorted(medians.items(), key=lambda x: x[1])
        cities_sorted = [item[0] for item in sorted_items]
        median_values = [item[1] for item in sorted_items]

        # Convert to English labels
        city_labels = [CITY_MAP.get(city, city) for city in cities_sorted]

        # Colors from base class
        colors = [self.city_colors.get(city, "#CCCCCC") for city in cities_sorted]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(city_labels, median_values, color=colors)

        # Add value labels
        for bar, value in zip(bars, median_values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value,
                f"{int(value):,}",
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold"
            )

        ax.set_title(
            f"Median {english_type} Price by City",
            fontsize=14,
            fontweight="bold"
        )

        ax.set_xlabel("City")
        ax.set_ylabel("Median Price (USD)")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()

        filename = (
            f"{self.base_path}"
            f"{english_type.lower().replace(' ', '_')}.png"
        )

        self.save_fig(fig, filename)

    def generate(self):
        """
        Generates:
        - Median sale price per city
        - Median monthly rent price per city
        """
        self._generate_for_type("იყიდება")
        self._generate_for_type("ქირავდება თვიურად")
