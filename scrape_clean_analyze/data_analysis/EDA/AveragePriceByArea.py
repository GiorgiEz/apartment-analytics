from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
import pandas as pd
import matplotlib.pyplot as plt


class AveragePriceByArea(DataAnalysis):
    def __init__(self):
        super().__init__()

    def run(self, city_name):
        """ Filters by 'იყიდება' transaction type and by the provided city name, then we crete the area bins
        and then group by the are_bin and calculate the average price """

        df = self.df[(self.df['transaction_type'] == 'იყიდება') & (self.df['city'] == city_name)].copy()

        bins = [0, 50, 100, 150, float('inf')]
        labels = ['0-50', '50-100', '100-150', '150+']
        df['area_bin'] = pd.cut(df['area_m2'], bins=bins, labels=labels, right=False)
        grouped = df.groupby('area_bin', observed=True)['price'].mean().reindex(labels)

        # Create a modern color palette
        colors = ['#3498DB', '#2ECC71', '#F39C12', '#E74C3C']  # Blue, Green, Orange, Red

        plt.figure(figsize=(10, 6))
        ax = grouped.plot(kind='bar', color=colors, edgecolor='white', linewidth=1.5, alpha=0.85)

        plt.title(f'Average Price by Area Range in {city_name} (For Sale Properties)',
                  fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('Area Range (m²)', fontsize=14, fontweight='bold')
        plt.ylabel('Average Price ($)', fontsize=14, fontweight='bold')
        plt.xticks(rotation=0, fontsize=12, fontweight='bold')

        # Add grid for better readability
        plt.grid(axis='y', linestyle='--', alpha=0.3)

        # Add value labels on bars
        for i, bar in enumerate(ax.patches):
            h = bar.get_height()
            if not pd.isna(h) and h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + (h * 0.01),
                        f"${int(h):,}", ha='center', va='bottom',
                        fontsize=11, fontweight='bold')

        # Remove chart borders for cleaner look
        for spine in plt.gca().spines.values():
            spine.set_visible(False)

        # Add light background
        plt.gca().set_facecolor('#f8f9fa')

        # Adjust y-axis to accommodate value labels
        if not grouped.isna().all():
            plt.ylim(0, max(grouped.dropna()) * 1.15)

        plt.tight_layout()
        output_path = self.image_path + f'price_by_area_bin_per_city_for_sale/{city_name}.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
