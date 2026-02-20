from data_analysis.DataAnalysis import DataAnalysis
from data_analysis.geo_to_eng_mappings import CITY_MAP
import matplotlib.pyplot as plt
import pandas as pd


class MedianPriceTrendOverTime(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.base_path = "time_analysis/price_trend/median_price_per_sqm_"

    def generate(self):
        """ Generates monthly median price per m^2 trends, separated by city. Uses ownership transactions only. """
        df_filtered = self.df[
            (self.df["price_per_sqm"] > 100) &
            (self.df["city"].notna()) &
            (self.df["upload_date"].notna()) &
            (self.df["transaction_type"].isin(["იყიდება", "გირავდება"]))
        ].copy()

        df_filtered["upload_date"] = pd.to_datetime(df_filtered["upload_date"], errors="coerce")

        df_filtered = df_filtered.dropna(subset=["upload_date"])
        df_filtered["year_month"] = df_filtered["upload_date"].dt.to_period("M")

        for city in df_filtered["city"].unique():
            city_df = df_filtered[df_filtered["city"] == city]
            grouped = (city_df.groupby("year_month")["price_per_sqm"].agg(["median", "count"]).sort_index())

            # Require minimum monthly volume
            grouped = grouped[grouped["count"] >= 100]

            if grouped.empty:
                continue

            grouped.index = grouped.index.to_timestamp()
            fig, ax = plt.subplots(figsize=self.figsize)

            color = self.city_colors.get(city, "#CCCCCC")
            ax.plot(grouped.index, grouped["median"], linewidth=2, color=color)

            english_city = CITY_MAP.get(city, city)

            ax.set_title(
                f"Median Price per m² Over Time - {english_city}",
                fontsize=14,
                fontweight="bold"
            )

            ax.set_xlabel("Month")
            ax.set_ylabel("Median Price per m² (USD)")

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            fig.autofmt_xdate()
            fig.tight_layout()

            filename = f"{self.base_path}{english_city.lower()}.png"
            self.save_fig(fig, filename)
