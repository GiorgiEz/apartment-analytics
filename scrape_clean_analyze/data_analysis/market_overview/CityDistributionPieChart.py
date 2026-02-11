from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
from scrape_clean_analyze.utils.geo_to_eng_mappings import CITY_MAP
import matplotlib.pyplot as plt


class CityDistributionPieChart(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.image_name = "market_overview/city_distribution_pie_chart.png"

    def generate(self):
        """ Generates pie chart, displaying apartment percentage and amount of each city """
        city_counts = self.df["city"].value_counts()
        colors = ["#AEC7E8", "#FFBB78", "#98DF8A"][:len(city_counts)]  # light blue, light orange, light green

        fig, ax = plt.subplots(figsize=(8, 8))

        ax.pie(
            city_counts.values,
            labels=[f"{CITY_MAP.get(city, city)}\n({city})" for city in city_counts.index],  # City names
            autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct / 100 * city_counts.sum()))})",  # Percentage values
            startangle=90,
            colors=colors,
            explode=[0.03] * len(city_counts),
            textprops={"fontsize": 12, "fontweight": "bold", "color": "black"},
        )

        ax.set_title(
            f"Apartment Distribution by City\nTotal listings: {len(self.df):,}",
            fontsize=14, fontweight="bold",
        )

        ax.axis("equal")
        self.save_fig(fig, self.image_name)
