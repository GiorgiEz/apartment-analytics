from data_analysis.DataAnalysis import DataAnalysis
from utils.geo_to_eng_mappings import CITY_MAP
import matplotlib.pyplot as plt


class ListingsByDistrictBarChart(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.base_path = "location_insights/districts_bar_charts/districts_in_"

    def generate(self):
        """ Generates horizontal bar charts showing the top 10 districts by listing count for each city. """
        df_filtered = self.df[
            self.df["district_name"].notna() &
            self.df["city"].notna()
        ].copy()

        for city in df_filtered["city"].unique():
            city_df = df_filtered[df_filtered["city"] == city]
            district_counts = (city_df["district_name"].value_counts().nlargest(10).sort_values(ascending=True))

            if district_counts.empty:
                continue

            fig, ax = plt.subplots(figsize=self.figsize)
            color = self.city_colors.get(city, "#CCCCCC")
            bars = ax.barh(district_counts.index, district_counts.values, color=color, alpha=0.85)

            # Add value labels
            for bar, value in zip(bars, district_counts.values):
                ax.text(
                    value,
                    bar.get_y() + bar.get_height() / 2,
                    f" {value:,}",
                    va="center",
                    fontsize=10,
                    fontweight="bold"
                )

            english_city = CITY_MAP.get(city, city)

            ax.set_title(
                f"Top 10 Districts by Listings - {english_city}",
                fontsize=14,
                fontweight="bold"
            )

            ax.set_xlabel("Number of Listings")
            ax.set_ylabel("District")

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            fig.tight_layout()

            filename = f"{self.base_path}{english_city.lower()}.png"
            self.save_fig(fig, filename)
