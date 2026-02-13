from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
from scrape_clean_analyze.utils.geo_to_eng_mappings import TRANSACTION_TYPE_MAP
import matplotlib.pyplot as plt
import numpy as np


class AreaDistributionHistogram(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.base_path = "apartment_characteristics/area_histograms/area_"

    def _generate_for_type(self, geo_transaction_type):
        # Filter relevant data
        df_filtered = self.df[
            (self.df["transaction_type"] == geo_transaction_type)
            & (self.df["area_m2"] > 15)
        ].copy()

        if df_filtered.empty:
            return

        english_type = TRANSACTION_TYPE_MAP.get(geo_transaction_type)
        areas = df_filtered["area_m2"].values

        if len(areas) < 10:
            return

        # Clip extreme outliers (99th percentile) for visualization only
        upper_limit = np.percentile(areas, 99)
        areas = areas[areas <= upper_limit]

        fig, ax = plt.subplots(figsize=self.figsize)
        ax.hist(areas, bins=40, alpha=0.7)

        ax.set_title(
            f"{english_type} Apartment Area Distribution\n"
            f"Listings: {len(areas):,}",
            fontsize=14,
            fontweight="bold"
        )

        ax.set_xlabel("Area (m²)")
        ax.set_ylabel("Count")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()

        filename = f"{self.base_path}" f"{english_type.lower().replace(' ', '_')}.png"
        self.save_fig(fig, filename)

    def generate(self):
        """
        Generates histograms of apartment area (m²),
        separately for Sale and Monthly Rent listings.
        """
        self._generate_for_type("იყიდება")
        self._generate_for_type("ქირავდება თვიურად")
