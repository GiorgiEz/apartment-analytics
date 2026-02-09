from scrape_clean_analyze.data_analysis.EDA.DataAnalysis import DataAnalysis
import seaborn as sns
import matplotlib.pyplot as plt


class AveragePriceByCity(DataAnalysis):
    def __init__(self):
        super().__init__()

    def run(self, output_path, transaction_type, city=''):
        """ Filters by provided transaction type, if city is provided then also filters by the city,
        and groups by street name, otherwise groups by the city and calculates the average price """

        filtered_df = self.df[(self.df['transaction_type'] == transaction_type)]

        if city:
            filtered_df = filtered_df[filtered_df['city'] == city]
            avg_prices = filtered_df.groupby('district_name')['price'].mean().sort_values(ascending=False).head(10)
        else:
            avg_prices = filtered_df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)

        # Check if we have data to plot
        if avg_prices.empty:
            print(f"No data available for {transaction_type} in {city if city else 'all cities'}")
            return

        # Create a custom color palette
        colors = sns.color_palette("husl", len(avg_prices))

        plt.figure(figsize=(12, 8))
        bars = plt.bar(range(len(avg_prices)), avg_prices.values, color=colors, edgecolor='white', linewidth=1.5,
                       alpha=0.85)

        # Set labels and title with improved styling
        if city:
            plt.title(f'Average Apartment Price in {city} by District ({transaction_type} only)',
                      fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('District Name', fontsize=14, fontweight='bold')
        else:
            plt.title(f'Average Apartment Price by City ({transaction_type} only)',
                      fontsize=16, fontweight='bold', pad=20)
            plt.xlabel('City', fontsize=14, fontweight='bold')

        plt.ylabel('Average Price ($)', fontsize=14, fontweight='bold')

        # Set x-ticks with improved visibility
        plt.xticks(range(len(avg_prices)), avg_prices.index, rotation=45, ha='right', fontsize=12, fontweight='bold')

        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height + (height * 0.01),
                     f'${int(height):,}', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Add grid for better readability
        plt.grid(axis='y', linestyle='--', alpha=0.3)

        # Remove chart borders for cleaner look
        for spine in plt.gca().spines.values():
            spine.set_visible(False)

        # Add light background
        plt.gca().set_facecolor('#f8f9fa')

        # Adjust y-axis to accommodate value labels
        plt.ylim(0, max(avg_prices.values) * 1.15)

        plt.tight_layout()
        plt.savefig(self.image_path + output_path, dpi=300, bbox_inches='tight')
        plt.close()
