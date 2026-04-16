from data_analysis.EDA.DataAnalysis import DataAnalysis
import matplotlib.pyplot as plt
import numpy as np



class LocationInsights(DataAnalysis):
    def __init__(self, sale_df, rent_df, combined_df):
        super().__init__()
        self.inner_dir = self.output_dir / "location_insights"
        self.inner_dir.mkdir(parents=True, exist_ok=True)
        self.sale_df = sale_df
        self.rent_df = rent_df
        self.df = combined_df

    def listings_by_district_bar_chart_generate(self):
        """
        Generates horizontal bar charts (top 10 districts) per city.
        Each image contains:
        - Left: Sale
        - Right: Rent
        """

        district_dir = self.inner_dir / "districts_bar_charts"
        district_dir.mkdir(parents=True, exist_ok=True)

        sale_df = self.sale_df.copy()
        rent_df = self.rent_df.copy()

        for city in self.cities:
            sale_df_copy = sale_df[sale_df["city"] == city]
            rent_df_copy = rent_df[rent_df["city"] == city]

            # Top 10 districts (highest first)
            sale_counts = sale_df_copy["district_name"].value_counts().nlargest(10)
            rent_counts = rent_df_copy["district_name"].value_counts().nlargest(10)

            if sale_counts.empty and rent_counts.empty:
                continue

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10), sharey=False)

            # --- SALE ---
            if not sale_counts.empty:
                sale_labels = [f"{i + 1:>2}. {name}" for i, name in enumerate(sale_counts.index)]

                bars1 = ax1.barh(sale_labels, sale_counts.values, color=self.transaction_colors["Sale"], alpha=0.85)

                for bar, value in zip(bars1, sale_counts.values):
                    ax1.text(value, bar.get_y() + bar.get_height() / 1.5, f" {value:,}",**self.styles["bar_label"])

                ax1.set_title(f"Sale\nListings: {sum(sale_counts)}", **self.styles["title"])
                ax1.invert_yaxis()

            # --- RENT ---
            if not rent_counts.empty:
                rent_labels = [f"{i + 1}. {name}" for i, name in enumerate(rent_counts.index)]

                bars2 = ax2.barh(rent_labels, rent_counts.values, color=self.transaction_colors["Rent"], alpha=0.85)

                for bar, value in zip(bars2, rent_counts.values):
                    ax2.text(value, bar.get_y() + bar.get_height() / 1.5, f" {value:,}", **self.styles["bar_label"])

                ax2.set_title(f"Rent\nListings: {sum(rent_counts)}", **self.styles["title"])
                ax2.invert_yaxis()

            # Axis labels
            ax1.set_xlabel("Listings", **self.styles["axis_title"])
            ax2.set_xlabel("Listings", **self.styles["axis_title"])
            ax1.set_ylabel("District", **self.styles["axis_title"])

            # Styling
            self.style_axes(ax1, fig, y_numeric=False)
            self.style_axes(ax2, fig, y_numeric=False)

            english_city = self.CITY_MAP.get(city, city)

            # Main title
            fig.suptitle(f"Top 10 Districts by Listings - {english_city}", **self.styles["suptitle"])

            self.save_fig(fig, district_dir / f"{english_city.lower()}.png")

    def price_per_sqm_by_district_boxplot_generate(self):
        """
        Generates horizontal boxplots of price per sqm for top districts per city.
        Each image contains:
        - Left: Sale
        - Right: Rent
        """
        boxplot_dir = self.inner_dir / "price_per_sqm_by_district_boxplots"
        boxplot_dir.mkdir(parents=True, exist_ok=True)

        for city in self.cities:
            sale_city_df = self.sale_df[self.sale_df["city"] == city]
            rent_city_df = self.rent_df[self.rent_df["city"] == city]

            if sale_city_df.empty and rent_city_df.empty:
                continue

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10), sharey=False)

            # ---------- SALE ----------
            if not sale_city_df.empty:
                top_districts = (sale_city_df["district_name"].value_counts().nlargest(8).index)

                district_data = []
                district_labels = []

                for district in top_districts:
                    values = sale_city_df[sale_city_df["district_name"] == district]["price_per_sqm"].values

                    if len(values) < 10:
                        continue

                    upper = np.percentile(values, 99)
                    values = values[values <= upper]

                    district_data.append(values)
                    district_labels.append(f"{district} ({len(values)})")

                if district_data:
                    medians = [np.median(v) for v in district_data]
                    sorted_idx = np.argsort(medians)[::-1]

                    district_data = [district_data[i] for i in sorted_idx]
                    district_labels = [district_labels[i] for i in sorted_idx]
                    medians = [medians[i] for i in sorted_idx]

                    boxplot = ax1.boxplot(district_data, labels=district_labels, showfliers=False, patch_artist=True, vert=False)

                    for patch in boxplot["boxes"]:
                        patch.set_facecolor(self.transaction_colors["Sale"])
                        patch.set_alpha(0.7)

                    for i, median in enumerate(medians):
                        ax1.scatter(median, i + 1, color="black", s=30, zorder=3)

                    ax1.set_title("Sale - Price per m²", **self.styles["title"])
                    ax1.invert_yaxis()

            # ---------- RENT ----------
            if not rent_city_df.empty:
                top_districts = (rent_city_df["district_name"].value_counts().nlargest(8).index)

                district_data = []
                district_labels = []

                for district in top_districts:
                    values = rent_city_df[rent_city_df["district_name"] == district]["price"].values

                    if len(values) < 10:
                        continue

                    upper = np.percentile(values, 99)
                    values = values[values <= upper]

                    district_data.append(values)
                    district_labels.append(f"{district} ({len(values)})")

                if district_data:
                    medians = [np.median(v) for v in district_data]
                    sorted_idx = np.argsort(medians)[::-1]

                    district_data = [district_data[i] for i in sorted_idx]
                    district_labels = [district_labels[i] for i in sorted_idx]
                    medians = [medians[i] for i in sorted_idx]

                    boxplot = ax2.boxplot(district_data, labels=district_labels, showfliers=False, patch_artist=True, vert=False)

                    for patch in boxplot["boxes"]:
                        patch.set_facecolor(self.transaction_colors["Rent"])
                        patch.set_alpha(0.7)

                    for i, median in enumerate(medians):
                        ax2.scatter(median, i + 1, color="black", s=30, zorder=3)

                    ax2.set_title("Rent - Price", **self.styles["title"])
                    ax2.invert_yaxis()

            # ---------- GLOBAL STYLING ----------
            english_city = self.CITY_MAP.get(city, city)

            fig.suptitle(f"Most expensive Districts in - {english_city}", **self.styles["suptitle"])

            ax1.set_xlabel("Price per m² (USD)", **self.styles["axis_title"])
            ax2.set_xlabel("Price (USD)", **self.styles["axis_title"])

            ax1.set_ylabel("District", **self.styles["axis_title"])

            # Disable numeric formatter on categorical axis
            self.style_axes(ax1, fig, y_numeric=False)
            self.style_axes(ax2, fig, y_numeric=False)

            self.save_fig(fig, boxplot_dir / f"{english_city.lower()}.png")

    def generate(self):
        self.listings_by_district_bar_chart_generate()
        self.price_per_sqm_by_district_boxplot_generate()