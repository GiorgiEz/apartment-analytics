from data_analysis.DataAnalysis import DataAnalysis
from utils.geo_to_eng_mappings import CITY_MAP
import matplotlib.pyplot as plt



class FloorDistributionBarChart(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.base_path = "apartment_characteristics/floor_bar_charts/floor_"

    def _bucket_floor(self, floor):
        if floor <= 2:
            return "1–2"
        elif floor <= 5:
            return "3–5"
        elif floor <= 9:
            return "6–9"
        elif floor <= 15:
            return "10–15"
        else:
            return "16+"

    def generate(self):
        """
        Generates floor distribution bar charts (bucketed),
        separated by transaction type and city.
        """
        df_filtered = self.df[(self.df["floor"] >= 0) & (self.df["floor"] <= 60) & (self.df["city"].notna())].copy()

        if df_filtered.empty:
            return

        # Create floor buckets
        df_filtered["floor_bucket"] = df_filtered["floor"].apply(self._bucket_floor)
        bucket_order = ["1–2", "3–5", "6–9", "10–15", "16+"]

        for city in df_filtered["city"].unique():
            city_df = df_filtered[df_filtered["city"] == city]
            counts = city_df["floor_bucket"].value_counts().reindex(bucket_order, fill_value=0)

            if counts.sum() < 10:
                continue

            fig, ax = plt.subplots(figsize=self.figsize)
            color = self.city_colors.get(city, "#CCCCCC")
            bars = ax.bar(counts.index, counts.values, color=color, alpha=0.8)

            # Add value labels
            for bar, value in zip(bars, counts.values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    value,
                    f"{value:,}",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    fontweight="bold"
                )

            english_city = CITY_MAP.get(city, city)
            ax.set_title(f"Floor Distribution - {english_city}", fontsize=14, fontweight="bold")

            ax.set_xlabel("Floor Range")
            ax.set_ylabel("Count")

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

            fig.tight_layout()
            filename = f"{self.base_path}" f"{english_city.lower()}.png"

            self.save_fig(fig, filename)
