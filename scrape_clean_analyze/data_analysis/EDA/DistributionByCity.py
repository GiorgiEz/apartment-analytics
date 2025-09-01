from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
import matplotlib.pyplot as plt


class DistributionByCity(DataAnalysis):
    def __init__(self):
        super().__init__()

    def run(self, output_path='city_distribution_pie.png'):
        """Counts listings per city and displays an enhanced pie chart with better visuals"""

        # Get city counts and handle cases with too many cities
        city_counts = self.df['city'].value_counts()

        # Create a more appealing color palette
        colors = ['#4C78A8', '#F58518', '#54A24B', '#E45756', '#72B7B2', '#B279A2', '#FF9DA6', '#9D755D']

        # Create figure with better proportions
        plt.figure(figsize=(12, 10))
        plt.grid(False)

        # Custom autopct function for better formatting
        def format_label(pct, all_vals):
            absolute = int(round(pct / 100 * sum(all_vals)))
            return f"{pct:.1f}%\n({absolute})"

        # Create the pie chart with labels inside
        wedges, texts, autotexts = plt.pie(
            city_counts,
            labels=city_counts.index,  # City names as labels
            autopct=lambda pct: format_label(pct, city_counts),
            startangle=90,
            colors=colors,
            shadow=True,
            explode=[0.03] * len(city_counts),  # Slightly separate all wedges
            textprops={'fontsize': 20, 'fontweight': 'bold'}
        )

        # Improve text appearance - make it larger and ensure good contrast
        for text in texts:
            text.set_fontsize(20)
            text.set_fontweight('bold')
            text.set_color('black')  # Set text color to white for darker backgrounds, black for lighter ones

        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(14)
            autotext.set_fontweight('bold')

        # Improve title
        plt.title(f'Apartment Listing Distribution by City\nTotal Apartments: {len(self.df):,}',
                  fontsize=20, fontweight='bold', pad=20
                  )

        plt.axis('equal')  # Ensure the pie is drawn as a circle
        plt.tight_layout()  # Adjust layout

        # Save with higher DPI for better quality
        plt.savefig(self.image_path + output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
