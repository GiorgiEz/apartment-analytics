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

        plt.figure(figsize=(8, 5))
        ax = grouped.plot(kind='bar', color='skyblue')
        plt.title(f'Average Price by Area Bin in {city_name} (იყიდება only)', fontsize=13)
        plt.xlabel('Area Range (m²)', fontsize=11)
        plt.ylabel('Average Price', fontsize=11)
        plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--', alpha=0.6)

        for i, bar in enumerate(ax.patches):
            h = bar.get_height()
            if not pd.isna(h) and h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h, f"{int(h):,}", ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        output_path = self.image_path + f'price_by_area_bin_per_city_for_sale/{city_name}.png'
        plt.savefig(output_path)
        plt.close()
