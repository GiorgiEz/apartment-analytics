from scrape_clean_analyze.data_analysis.EDA.DataAnalysis import DataAnalysis
import matplotlib.pyplot as plt


class AveragePricePerSQM(DataAnalysis):
    def __init__(self):
        super().__init__()

    def run(self, output_path='avg_price_per_sqm_by_city.png'):
        """ Filter by 'იყიდება', then we group by city and find average price_per_sqm """

        filtered_df = self.df[self.df['transaction_type'] == 'იყიდება'].copy()
        avg_price_per_sqm = filtered_df.groupby('city')['price_per_sqm'].mean().sort_values()

        # Create a custom color palette
        colors = ['#2E86AB', '#A23B72', '#F18F01']  # Modern, harmonious colors

        plt.figure(figsize=(10, 8))

        # Create bar plot with improved styling
        bars = plt.bar(avg_price_per_sqm.index, avg_price_per_sqm.values,
                       color=colors[:len(avg_price_per_sqm)],
                       edgecolor='white', linewidth=2, alpha=0.85)

        # Add value labels on top of bars
        for i, (city, value) in enumerate(avg_price_per_sqm.items()):
            plt.text(i, value + (value * 0.01), f'${value:,.0f}',
                     ha='center', va='bottom', fontsize=12, fontweight='bold')

        # Add a horizontal grid for better readability
        plt.grid(axis='y', alpha=0.3, linestyle='--')

        # Style the plot
        plt.title('Average Price per Square Meter by City (For Sale Properties)',
                  fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('City', fontsize=14, fontweight='bold')
        plt.ylabel('Price per m² ($)', fontsize=14, fontweight='bold')

        # Increase font size of city names on x-axis
        plt.xticks(fontsize=13, fontweight='bold')

        # Remove spines for a cleaner look
        for spine in plt.gca().spines.values():
            spine.set_visible(False)

        # Add a subtle background
        plt.gca().set_facecolor('#f8f9fa')

        # Adjust y-axis to give some headroom for the value labels
        plt.ylim(0, max(avg_price_per_sqm.values) * 1.1)

        plt.tight_layout()
        plt.savefig(self.image_path + output_path, dpi=300, bbox_inches='tight')
        plt.close()
