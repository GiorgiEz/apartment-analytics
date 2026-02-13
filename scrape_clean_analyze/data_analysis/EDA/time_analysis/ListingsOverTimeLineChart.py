from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
import matplotlib.pyplot as plt
import pandas as pd


class ListingsOverTimeLineChart(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.image_name = "time_analysis/listings_over_time.png"

    def generate(self):
        """
        Generates a monthly aggregated line chart showing the number
        of listings over time. Provides insight into overall market
        activity trends and seasonality.
        """

        df_filtered = self.df[self.df["upload_date"].notna()].copy()

        # Convert to datetime
        df_filtered["upload_date"] = pd.to_datetime(df_filtered["upload_date"], errors="coerce")
        df_filtered = df_filtered.dropna(subset=["upload_date"])

        # Monthly aggregation
        df_filtered["year_month"] = df_filtered["upload_date"].dt.to_period("M")

        monthly_counts = (
            df_filtered
            .groupby("year_month")
            .size()
            .sort_index()
        )

        if monthly_counts.empty:
            return

        # Convert period to timestamp for plotting
        monthly_counts.index = monthly_counts.index.to_timestamp()

        fig, ax = plt.subplots(figsize=self.figsize)
        ax.plot(monthly_counts.index, monthly_counts.values, linewidth=2)

        ax.set_title("Listings Over Time (Monthly)", fontsize=14, fontweight="bold")

        ax.set_xlabel("Month")
        ax.set_ylabel("Number of Listings")

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        fig.autofmt_xdate()
        fig.tight_layout()

        self.save_fig(fig, self.image_name)
