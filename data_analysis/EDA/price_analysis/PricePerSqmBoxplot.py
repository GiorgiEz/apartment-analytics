from data_analysis.DataAnalysis import DataAnalysis
from utils.geo_to_eng_mappings import CITY_MAP, TRANSACTION_TYPE_MAP
import matplotlib.pyplot as plt
import numpy as np


class PricePerSqmBoxplot(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.base_path = "price_analysis/price_per_sqm_boxplots/price_per_sqm_"

    def _generate_for_type(self, geo_transaction_type):
        """
        Generates box plots of price per square meter by city, separately for Sale and Monthly Rent listings.
        Highlights median, spread, and relative affordability differences across cities.
        """
        # Filter relevant data
        df_filtered = self.df[
            (self.df["transaction_type"] == geo_transaction_type)
            & (self.df["price_per_sqm"] > 0)
            & (self.df["city"].notna())
        ].copy()

        if df_filtered.empty:
            return

        english_type = TRANSACTION_TYPE_MAP.get(geo_transaction_type)

        city_data = []
        city_labels = []

        # Prepare boxplot data per city
        for city in df_filtered["city"].unique():
            city_df = df_filtered[df_filtered["city"] == city]
            values = city_df["price_per_sqm"].values

            if len(values) < 10:
                continue

            # Clip extreme outliers (99th percentile)
            upper_limit = np.percentile(values, 99)
            values = values[values <= upper_limit]

            city_data.append(values)
            city_labels.append(CITY_MAP.get(city, city))

        if not city_data:
            return

        # Sort cities by median price_per_sqm
        sorted_indices = np.argsort([np.median(values) for values in city_data])

        city_data = [city_data[i] for i in sorted_indices]
        city_labels = [city_labels[i] for i in sorted_indices]

        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)

        boxplot = ax.boxplot(city_data, labels=city_labels, showfliers=False, patch_artist=True)
        # Apply city-specific colors
        for patch, label in zip(boxplot["boxes"], city_labels):
            # Convert English label back to Georgian to fetch correct color
            geo_city = next((k for k, v in CITY_MAP.items() if v == label), None)
            color = self.city_colors.get(geo_city, "#CCCCCC")

            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_title(f"{english_type} Price per m² by City", fontsize=14, fontweight="bold")

        ax.set_xlabel("City")
        ax.set_ylabel("Price per m² (USD)")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.tight_layout()

        filename = f"{self.base_path}" f"{english_type.lower().replace(' ', '_')}.png"
        self.save_fig(fig, filename)

    def generate(self):
        """ Generates two boxplots:
        - Sale price per sqm by city
        - Monthly rent price per sqm by city
        """

        self._generate_for_type("იყიდება")          # Sale
        self._generate_for_type("ქირავდება თვიურად")  # Monthly Rent
