from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
import seaborn as sns
import matplotlib.pyplot as plt


class AveragePricePerSQM(DataAnalysis):
    def __init__(self):
        super().__init__()

    def run(self, output_path='avg_price_per_sqm_by_city.png'):
        """ Filter by 'იყიდება', then we group by city and find average price_per_sqm """

        filtered_df = self.df[self.df['transaction_type'] == 'იყიდება'].copy()
        avg_price_per_sqm = filtered_df.groupby('city')['price_per_sqm'].mean().sort_values()

        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x=avg_price_per_sqm.index, y=avg_price_per_sqm.values,
                         palette='viridis', hue=avg_price_per_sqm.index)

        plt.title('Average Price per m² by City (იყიდება only)', fontsize=14)
        plt.xlabel('City', fontsize=12)
        plt.ylabel('Average Price per m²', fontsize=12)
        plt.xticks(rotation=30, ha='right')

        for bar in ax.patches:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h, f"{int(h):,}", ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.savefig(self.image_path + output_path)
        plt.close()
