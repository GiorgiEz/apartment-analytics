from data_analysis.DataAnalysis import DataAnalysis
from data_analysis.geo_to_eng_mappings import CITY_MAP
import matplotlib.pyplot as plt
import numpy as np


class PricePerSqmByDistrictBoxplot(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.base_path = "location_insights/price_per_sqm_by_district_boxplots/"

    def generate(self):
        """ Generates box plots of price per square meter for top districts (by listing count) within each city. """
        # Only Sale + Mortgage together = ownership market
        df_filtered = self.df[
            (self.df["price_per_sqm"] > 100) &
            (self.df["district_name"].notna()) &
            (self.df["city"].notna()) &
            (self.df["transaction_type"].isin(["იყიდება", "გირავდება"]))
            ].copy()

        for city in df_filtered["city"].unique():
            city_df = df_filtered[df_filtered["city"] == city]

            # Select top 8 districts by listing count
            top_districts = city_df["district_name"].value_counts().nlargest(8).index
            city_df = city_df[city_df["district_name"].isin(top_districts)]

            if city_df.empty:
                continue

            district_data = []
            district_labels = []

            for district in top_districts:
                district_prices = city_df[city_df["district_name"] == district]["price_per_sqm"].values

                if len(district_prices) < 10:
                    continue

                # Clip top 1% (visual only)
                upper_limit = np.percentile(district_prices, 99)
                district_prices = district_prices[district_prices <= upper_limit]

                district_data.append(district_prices)
                district_labels.append(district)

            if not district_data:
                continue

            # Sort by median price
            sorted_indices = np.argsort([np.median(values) for values in district_data])

            district_data = [district_data[i] for i in sorted_indices]
            district_labels = [district_labels[i] for i in sorted_indices]

            fig, ax = plt.subplots(figsize=self.figsize)

            boxplot = ax.boxplot(
                district_data,
                labels=district_labels,
                showfliers=False,
                patch_artist=True,
                vert=False
            )

            # Apply city color
            color = self.city_colors.get(city, "#CCCCCC")

            for patch in boxplot["boxes"]:
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

            english_city = CITY_MAP.get(city, city)

            ax.set_title(
                f"Price per m² by District - {english_city} (For Sale + Mortgages Only)",
                fontsize=14,
                fontweight="bold"
            )

            ax.set_xlabel("Price per m² (USD)")
            ax.set_ylabel("District")

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            fig.tight_layout()

            filename = f"{self.base_path}{english_city.lower()}.png"
            self.save_fig(fig, filename)
