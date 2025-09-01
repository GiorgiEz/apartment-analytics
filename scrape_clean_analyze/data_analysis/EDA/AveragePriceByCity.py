from scrape_clean_analyze.data_analysis.DataAnalysis import DataAnalysis
import seaborn as sns
import matplotlib.pyplot as plt


class AveragePriceByCity(DataAnalysis):
    def __init__(self):
        super().__init__()

    def run(self, output_path, transaction_type, city=''):
        """ Filters by provided transaction type, if city is provided then also filters by the city,
        and groups by street name, otherwise groups by the city and calculates the average price """

        filtered_df = self.df[(self.df['transaction_type'] == transaction_type)
                              & (self.df['district_name'] != "არ არის მოწოდებული")]

        if city:
            filtered_df = filtered_df[filtered_df['city'] == city]
            avg_prices = filtered_df.groupby('district_name')['price'].mean().sort_values(ascending=False).head(10)
        else:
            avg_prices = filtered_df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)

        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x=avg_prices.index, y=avg_prices.values, palette='viridis', hue=avg_prices.index)

        if city:
            plt.title(f'Average Apartment Price in {city} by street ({transaction_type} only)')
            plt.xlabel('street name')
        else:
            plt.title(f'Average Apartment Price by city ({transaction_type} only)')
            plt.xlabel('city')
        plt.ylabel('Average Price')
        plt.xticks(rotation=30, ha='right')

        for i, bar in enumerate(ax.patches):
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h, f"{int(h):,}", ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        plt.savefig(self.image_path + output_path)
        plt.close()