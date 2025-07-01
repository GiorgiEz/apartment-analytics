import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



class DataAnalysis:
    def __init__(self):
        conn = sqlite3.connect('database/apartments.db')
        self.df = pd.read_sql_query("SELECT * FROM apartments", conn)  # Gets all the data from the apartments.db
        conn.close()

        self.image_path = 'frontend/charts/'
        self.transaction_types = ['იყიდება', 'ქირავდება დღიურად', 'ქირავდება თვიურად', 'გირავდება']

    def __plot_listing_distribution_by_city(self, output_path='city_distribution_pie.png'):
        # Count listings per city
        city_counts = self.df['city'].value_counts()

        # Plot pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(
            city_counts,
            labels=city_counts.index,
            autopct='%1.1f%%',
            startangle=140,
            colors=sns.color_palette('pastel')[:len(city_counts)],
            textprops={'fontsize': 15}
        )

        plt.title('Apartment Listing Distribution by City')
        plt.tight_layout()
        plt.savefig(self.image_path + output_path)
        plt.close()

    def __avg_price_by_city(self, output_path, transaction_type, city=''):
        filtered_df = self.df[self.df['transaction_type'] == transaction_type]  # Filter by transaction type

        # Group by city and calculate average price
        if city:
            filtered_df = filtered_df[filtered_df['city'] == city]
            avg_prices = filtered_df.groupby('street_name')['price'].mean().sort_values(ascending=False).head(10)
        else:
            avg_prices = filtered_df.groupby('city')['price'].mean().sort_values(ascending=False).head(10)

        plt.figure(figsize=(10, 6))
        ax = sns.barplot(x=avg_prices.index, y=avg_prices.values, palette='viridis', hue=avg_prices.index)

        plt.title(f'Average Apartment Price by City ({transaction_type} only)')
        plt.xlabel('City')
        plt.ylabel('Average Price')
        plt.xticks(rotation=30, ha='right')

        # Add price labels on top of bars
        for i, bar in enumerate(ax.patches):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height, f"{int(height):,}",  # formatted with comma
                ha='center', va='bottom', fontsize=9
            )

        plt.tight_layout()
        plt.savefig(self.image_path + output_path)
        plt.close()

    def main(self):
        self.__plot_listing_distribution_by_city()

        # Compare average apartment prices by cities for every transaction types
        for transaction_type in self.transaction_types:
            self.__avg_price_by_city(f'avg_price_by_city/{transaction_type}.png', transaction_type)

        # Compare average apartment prices in a specific city for every transaction types
        for city_name in ['ქუთაისი', 'თბილისი', 'ბათუმი']:
            for transaction_type in self.transaction_types:
                self.__avg_price_by_city(f'avg_price_by_street/{city_name}/{transaction_type}.png',
                                         transaction_type, city_name)

