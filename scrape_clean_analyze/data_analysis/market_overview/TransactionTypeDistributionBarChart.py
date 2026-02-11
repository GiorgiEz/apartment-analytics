from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
from scrape_clean_analyze.utils.geo_to_eng_mappings import TRANSACTION_TYPE_MAP
import matplotlib.pyplot as plt


class TransactionTypeDistributionBarChart(DataAnalysis):
    def __init__(self, df, output_dir):
        super().__init__(df, output_dir)
        self.image_name = "market_overview/transaction_type_distribution_bar_chart.png"

    def generate(self):
        """ Generates horizontal bar chart displaying market composition by transaction type. """
        # Map Georgian transaction types to English
        mapped_series = self.df["transaction_type"].map(lambda x: TRANSACTION_TYPE_MAP.get(x, x))
        transaction_counts = mapped_series.value_counts()  # Count occurrences

        desired_order = ["For Sale", "Monthly Rent", "Daily Rent", "Mortgage"]  # Logical order
        transaction_counts = transaction_counts.reindex(desired_order).dropna()

        fig, ax = plt.subplots(figsize=(10, 6))

        # Add value labels to bars
        for i, value in enumerate(transaction_counts.values):
            ax.text(value, i,f" {value:,}", va="center", fontsize=11, fontweight="bold")

        # Title and labels
        ax.set_title(f"Market Composition by Transaction Type\nTotal listings: {len(self.df):,}",
            fontsize=14, fontweight="bold")

        ax.set_xlabel("Number of Listings")
        ax.set_ylabel("Transaction Type")

        # Clean layout
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        self.save_fig(fig, self.image_name)
