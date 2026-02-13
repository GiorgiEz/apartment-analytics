from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
from scrape_clean_analyze.utils.geo_to_eng_mappings import TRANSACTION_TYPE_MAP
import matplotlib.pyplot as plt
import numpy as np


class BedroomsVsPriceBoxplot(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.base_path = "apartment_characteristics/bedrooms_vs_price_boxplot/"

    def _generate_for_type(self, geo_transaction_type):
        # Filter relevant data
        df_filtered = self.df[
            (self.df["transaction_type"] == geo_transaction_type)
            & (self.df["price"] > 0)
            & (self.df["bedrooms"] > 0)
        ].copy()

        # Uses logical minimums for prices
        if geo_transaction_type == "იყიდება":
            df_filtered = df_filtered[df_filtered["price"] >= 10_000]
        else:
            df_filtered = df_filtered[df_filtered["price"] >= 100]

        if df_filtered.empty:
            return

        # Restricts extreme bedroom counts
        df_filtered = df_filtered[df_filtered["bedrooms"] <= 6]
        english_type = TRANSACTION_TYPE_MAP.get(geo_transaction_type)

        bedroom_groups = []
        bedroom_labels = []

        for bedrooms in sorted(df_filtered["bedrooms"].unique()):
            prices = df_filtered[df_filtered["bedrooms"] == bedrooms]["price"].values

            if len(prices) < 10:
                continue

            # Clip extreme prices (99th percentile)
            upper_limit = np.percentile(prices, 99)
            prices = prices[prices <= upper_limit]

            bedroom_groups.append(prices)
            bedroom_labels.append(str(int(bedrooms)))

        if not bedroom_groups:
            return

        fig, ax = plt.subplots(figsize=self.figsize)
        boxplot = ax.boxplot(bedroom_groups, labels=bedroom_labels, showfliers=False, patch_artist=True)

        # Uniform styling
        for patch in boxplot["boxes"]:
            patch.set_alpha(0.6)

        ax.set_title(
            f"{english_type} Price by Number of Bedrooms",
            fontsize=14,
            fontweight="bold"
        )

        ax.set_xlabel("Bedrooms")
        ax.set_ylabel("Price (USD)")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.tight_layout()
        filename = f"{self.base_path}" f"{english_type.lower().replace(' ', '_')}.png"

        self.save_fig(fig, filename)

    def generate(self):
        """
        Generates box plots showing price distribution by number of bedrooms,
        separately for Sale and Monthly Rent listings.
        """
        self._generate_for_type("იყიდება")
        self._generate_for_type("ქირავდება თვიურად")
