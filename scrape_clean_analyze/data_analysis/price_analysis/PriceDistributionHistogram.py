from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
from scrape_clean_analyze.utils.geo_to_eng_mappings import CITY_MAP, TRANSACTION_TYPE_MAP
import matplotlib.pyplot as plt
import numpy as np


class PriceDistributionHistogram(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.base_path = "price_analysis/price_histograms/price_"

    def _kde(self, data, grid_points=1000):
        data = np.array(data)
        xmin, xmax = data.min(), data.max()
        x_grid = np.linspace(xmin, xmax, grid_points)

        bandwidth = 1.06 * data.std() * (len(data) ** (-1 / 5))
        kde_values = np.zeros_like(x_grid)

        for value in data:
            kde_values += np.exp(-0.5 * ((x_grid - value) / bandwidth) ** 2)

        kde_values /= (len(data) * bandwidth * np.sqrt(2 * np.pi))
        return x_grid, kde_values

    def generate(self):
        """
        Generates histogram and KDE plots of apartment prices, separated by transaction type and city.
        Provides insight into typical price ranges, distribution shape, and market spread.
        """
        # Clean data
        df_clean = self.df.dropna(subset=["price", "city", "transaction_type"])
        df_clean = df_clean[df_clean["price"] > 0]

        # Keep only Sale + Monthly Rent
        allowed_types_geo = ["იყიდება", "ქირავდება თვიურად"]
        df_clean = df_clean[df_clean["transaction_type"].isin(allowed_types_geo)]

        for geo_type in allowed_types_geo:
            english_type = TRANSACTION_TYPE_MAP.get(geo_type)
            type_df = df_clean[df_clean["transaction_type"] == geo_type]

            for city in type_df["city"].unique():
                city_df = type_df[type_df["city"] == city]
                prices = city_df["price"].values
                color = self.city_colors.get(city, "#CCCCCC")

                if len(prices) < 10:
                    continue  # avoid meaningless charts

                # remove extreme outliers (99th percentile)
                upper_limit = np.percentile(prices, 99)
                prices = prices[prices <= upper_limit]

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(prices, bins=40, alpha=0.6, color=color)

                # KDE
                x_kde, y_kde = self._kde(prices)
                ax2 = ax.twinx()
                ax2.plot(x_kde, y_kde, color=color, linewidth=2)
                ax2.set_yticks([])

                english_city = CITY_MAP.get(city, city)

                ax.set_title(
                    f"{english_type} Price Distribution - {english_city}\n"
                    f"Listings: {len(city_df):,}",
                    fontsize=14,
                    fontweight="bold"
                )

                ax.set_xlabel("Price (USD)")
                ax.set_ylabel("Count")

                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)

                filename = (
                    f"{self.base_path}"
                    f"{english_type.lower().replace(' ', '_')}_"
                    f"{english_city.lower()}.png"
                )

                self.save_fig(fig, filename)
