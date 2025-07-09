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
        self.cities = ['ქუთაისი', 'თბილისი', 'ბათუმი']

    def __plot_listing_distribution_by_city(self, output_path='city_distribution_pie.png'):
        """ Counts listings per city and displays the pie chart """

        city_counts = self.df['city'].value_counts()

        plt.figure(figsize=(8, 8))
        plt.pie(
            city_counts, labels=city_counts.index, autopct='%1.1f%%', startangle=140,
            colors=sns.color_palette('pastel')[:len(city_counts)], textprops={'fontsize': 15}
        )

        plt.title('Apartment Listing Distribution by City')
        plt.tight_layout()
        plt.savefig(self.image_path + output_path)
        plt.close()

    def __avg_price_by_city(self, output_path, transaction_type, city=''):
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

    def __plot_avg_price_by_area_bins_per_city(self, city_name):
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

    def __plot_avg_price_per_sqm_by_city(self, output_path='avg_price_per_sqm_by_city.png'):
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

    def main(self):
        self.__plot_listing_distribution_by_city()
        self.__plot_avg_price_per_sqm_by_city()

        for city_name in self.cities:
            self.__plot_avg_price_by_area_bins_per_city(city_name)

        # Compare average apartment prices by cities for every transaction types
        for transaction_type in self.transaction_types:
            self.__avg_price_by_city(f'avg_price_by_city/{transaction_type}.png', transaction_type)

        # Compare average apartment prices in a specific city for every transaction types
        for city_name in self.cities:
            for transaction_type in self.transaction_types:
                self.__avg_price_by_city(f'avg_price_by_street/{city_name}/{transaction_type}.png',
                                         transaction_type, city_name)

