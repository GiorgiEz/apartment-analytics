from data_analysis.EDA.DataAnalysis import DataAnalysis
import matplotlib.pyplot as plt
import numpy as np



class PriceAnalysis(DataAnalysis):
    def __init__(self, sale_df, rent_df, combined_df):
        super().__init__()
        self.inner_dir = self.output_dir / "price_analysis"
        self.inner_dir.mkdir(parents=True, exist_ok=True)
        self.sale_df = sale_df
        self.rent_df = rent_df
        self.df = combined_df

    def median_bar_charts_generate(self, df, title):
        """
        Generates a bar chart of median apartment prices by city.

        Parameters:
        - df: filtered dataframe (e.g. sale_df or rent_df)
        - title: chart title (e.g. "Median Sale Price by City")
        - filename: output filename
        """
        median_dir = self.inner_dir / "median_bar_charts"
        median_dir.mkdir(parents=True, exist_ok=True)

        # Compute medians
        medians = {}
        for city in self.cities:
            city_prices = df[df["city"] == city]["price"].values
            medians[self.CITY_MAP.get(city, city)] = {"median": np.median(city_prices), "count": len(city_prices)}

        # Sort cities by median
        sorted_items = sorted(medians.items(), key=lambda x: x[1]["median"])
        cities_sorted = [item[0] for item in sorted_items]
        median_values = [item[1]["median"] for item in sorted_items]
        listings_count = [item[1]["count"] for item in sorted_items]
        max_height = median_values[-1]

        # Labels + colors
        colors = [self.city_colors.get(city, "#CCCCCC") for city in cities_sorted]

        fig, ax = plt.subplots(figsize=self.figsize)
        bars = ax.bar(cities_sorted, median_values, color=colors)
        offset = self.bar_label_offset(max_height)

        # Value labels
        for i, val in enumerate(zip(bars, median_values)):
            bar, value = val
            ax.text(bar.get_x() + bar.get_width() / 2, value + offset, f"{int(value):}$", **self.styles["bar_label"])
            ax.text(bar.get_x() + bar.get_width() / 2, value - offset * 4, f"Listings: {listings_count[i]}", **self.styles["bar_label"])

        # Styling
        ax.set_title(f"Median {title} Price by City", **self.styles["title"])

        ax.set_xlabel("City", **self.styles["axis_title"])
        ax.set_ylabel("Median Price (USD)", **self.styles["axis_title"])

        self.style_axes(ax, fig, max_height)

        self.save_fig(fig, median_dir / title.lower())

    def price_histograms_generate(self):
        """ Generates 1 histogram per city with two subplots: Sale and Rent distributions, each with KDE overlay. """
        def _kde(data, grid_points=1000):
            data = np.array(data)
            xmin, xmax = data.min(), data.max()
            x_grid = np.linspace(xmin, xmax, grid_points)

            bandwidth = 1.06 * data.std() * (len(data) ** (-1 / 5))
            kde_values = np.zeros_like(x_grid)

            for value in data:
                kde_values += np.exp(-0.5 * ((x_grid - value) / bandwidth) ** 2)

            kde_values /= (len(data) * bandwidth * np.sqrt(2 * np.pi))
            return x_grid, kde_values

        histogram_dir = self.inner_dir / "price_histograms"
        histogram_dir.mkdir(parents=True, exist_ok=True)

        for city in self.cities:
            sale_prices = self.sale_df[self.sale_df["city"] == city]["price"].values
            rent_prices = self.rent_df[self.rent_df["city"] == city]["price"].values

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8), sharey=True)

            city_color = self.city_colors.get(city, "#CCCCCC")

            # SALE
            counts_sale, bins_sale, _ = ax1.hist(sale_prices, bins=40, color=city_color, alpha=0.7)

            x_sale, y_sale = _kde(sale_prices)

            # scale KDE to histogram
            bin_width_sale = bins_sale[1] - bins_sale[0]
            y_sale *= len(sale_prices) * bin_width_sale

            ax1.plot(x_sale, y_sale, color=self.transaction_colors.get("Sale", "#2e7d32"), linewidth=2)

            ax1.set_title("Sale", **self.styles["title"])
            ax1.text(0.5, 0.98, f"Listings: {len(sale_prices)}", transform=ax1.transAxes, ha="center", fontsize=12)

            # RENT
            counts_rent, bins_rent, _ = ax2.hist(rent_prices, bins=40, color=city_color, alpha=0.7)

            x_rent, y_rent = _kde(rent_prices)

            # scale KDE to histogram
            bin_width_rent = bins_rent[1] - bins_rent[0]
            y_rent *= len(rent_prices) * bin_width_rent

            ax2.plot(x_rent, y_rent, color=self.transaction_colors.get("Rent", "#2e7d32"), linewidth=2)

            ax2.set_title("Rent", **self.styles["title"])
            ax2.text(0.5, 0.98, f"Listings: {len(rent_prices)}", transform=ax2.transAxes, ha="center", fontsize=12)

            # Shared Y
            ax1.set_ylabel("Count", **self.styles["axis_title"])

            # X labels
            ax1.set_xlabel("Price (USD)", **self.styles["axis_title"])
            ax2.set_xlabel("Price (USD)", **self.styles["axis_title"])

            # Styling
            self.style_axes(ax1, fig, max_height=counts_sale.max())
            self.style_axes(ax2, fig, max_height=counts_rent.max())

            english_city = self.CITY_MAP.get(city, city)

            fig.suptitle(f"Price Distribution - {english_city}", **self.styles["suptitle"])

            self.save_fig(fig, histogram_dir / f"{english_city.lower()}.png")

    def price_per_sqm_box_plots_generate(self, df, title):
        """
        Generates boxplot of price per sqm by city.
        """

        boxplot_dir = self.inner_dir / "price_per_sqm_boxplots"
        boxplot_dir.mkdir(parents=True, exist_ok=True)

        city_data = []
        city_labels = []
        cities_used = []

        for city in self.cities:
            values = df[df["city"] == city]["price_per_sqm"].values

            if len(values) < 10:
                continue

            # Clip outliers (consistent with your other charts)
            upper = np.percentile(values, 99)
            values = values[values <= upper]

            city_data.append(values)
            city_labels.append(self.CITY_MAP.get(city, city))
            cities_used.append(city)

        if not city_data:
            return

        # Sort by median (descending)
        medians = [np.median(v) for v in city_data]
        sorted_idx = np.argsort(medians)[::-1]

        city_data = [city_data[i] for i in sorted_idx]
        city_labels = [city_labels[i] for i in sorted_idx]
        cities_used = [cities_used[i] for i in sorted_idx]
        medians = [medians[i] for i in sorted_idx]

        # Plot
        fig, ax = plt.subplots(figsize=self.figsize)

        boxplot = ax.boxplot(city_data,labels=city_labels,showfliers=False,patch_artist=True)

        # Colors (use original city keys)
        for patch, city in zip(boxplot["boxes"], cities_used):
            patch.set_facecolor(self.city_colors.get(city, "#CCCCCC"))
            patch.set_alpha(0.7)

        # Median markers (recommended)
        for i, median in enumerate(medians):
            ax.scatter(i + 1, median, color="black", s=30, zorder=3)

        # Title
        ax.set_title(f"Price Per m² by City for {title}\nListings: {len(df):,}", **self.styles["title"])

        ax.set_xlabel("City", **self.styles["axis_title"])
        ax.set_ylabel("Price per m² (USD)", **self.styles["axis_title"])

        # Styling
        max_height = max([max(v) for v in city_data])
        self.style_axes(ax, max_height=max_height)

        self.save_fig(fig, boxplot_dir / f"{title.lower()}.png")

    def feature_vs_price_scatter_plots(self, feature):
        """ Generates side-by-side scatter plots """
        feature_scatter_plot_dir = self.inner_dir / "feature_vs_price_scatter"
        feature_scatter_plot_dir.mkdir(parents=True, exist_ok=True)

        sale_df = self.sale_df.copy()
        rent_df = self.rent_df.copy()

        lower, upper = sale_df[feature].quantile(0.001), sale_df[feature].quantile(0.999)
        sale_df = sale_df[(sale_df[feature] >= lower) & (sale_df[feature] <= upper)]

        lower, upper = rent_df[feature].quantile(0.001), rent_df[feature].quantile(0.999)
        rent_df = rent_df[(rent_df[feature] >= lower) & (rent_df[feature] <= upper)]

        # Extract values
        x_sale = sale_df[feature].values
        y_sale = sale_df["price"].values

        x_rent = rent_df[feature].values
        y_rent = rent_df["price"].values

        # Create subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), sharey=False)

        # --- SALE
        ax1.scatter(x_sale, y_sale, s=8, alpha=0.3, color=self.transaction_colors["Sale"])

        ax1.set_title(f"Sale\nListings: {len(x_sale):,}", **self.styles["title"])

        ax1.set_xlabel(feature.capitalize(), **self.styles["axis_title"])
        ax1.set_ylabel("Price (USD)", **self.styles["axis_title"])

        # --- RENT
        ax2.scatter(x_rent, y_rent, s=8, alpha=0.3, color=self.transaction_colors["Rent"])

        ax2.set_title(f"Rent\nListings: {len(x_rent):,}", **self.styles["title"])

        ax2.set_xlabel(feature.capitalize(), **self.styles["axis_title"])

        # Styling
        self.style_axes(ax1, max_height=None)
        self.style_axes(ax2, max_height=None)

        # Main title
        fig.suptitle(f"{feature.capitalize()} vs Price", **self.styles["suptitle"])

        self.save_fig(fig, feature_scatter_plot_dir / f"{feature}_vs_price.png")

    def generate(self):
        # Median bar charts
        self.median_bar_charts_generate(self.sale_df, "Sale")
        self.median_bar_charts_generate(self.rent_df, "Rent")

        # Price Histograms
        self.price_histograms_generate()

        # Price Per SQM box plots
        self.price_per_sqm_box_plots_generate(self.sale_df, "Sale")
        self.price_per_sqm_box_plots_generate(self.rent_df, "Rent")

        # Feature vs Price scatter plots
        self.feature_vs_price_scatter_plots("area_m2")
        self.feature_vs_price_scatter_plots("floor")
