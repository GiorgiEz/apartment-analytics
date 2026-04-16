from data_analysis.EDA.DataAnalysis import DataAnalysis
import matplotlib.pyplot as plt
import numpy as np



class ApartmentCharacteristics(DataAnalysis):
    """Apartment Characteristics class used to generate area histograms, bedrooms box plots and floor bar charts."""
    def __init__(self, sale_df, rent_df, combined_df):
        super().__init__()
        self.inner_dir = self.output_dir / "apartment_characteristics"
        self.inner_dir.mkdir(parents=True, exist_ok=True)
        self.sale_df = sale_df
        self.rent_df = rent_df
        self.df = combined_df

    def area_distribution_histogram_generate(self, df, title):
        """
        Generates histogram of apartment area (m²).

        Parameters:
        - df: filtered dataframe (sale_df or rent_df)
        - title: "Sale" or "Rent"
        """

        histogram_dir = self.inner_dir / "area_histograms"
        histogram_dir.mkdir(parents=True, exist_ok=True)

        areas = df["area_m2"].values

        # Clip extreme outliers (99th percentile)
        upper_limit = np.quantile(areas, 0.995)
        areas = areas[areas <= upper_limit]

        # Plot
        fig, ax = plt.subplots(figsize=self.figsize)
        counts, bins, _ = ax.hist(areas, bins=40, alpha=0.7, color=self.transaction_colors[title])
        max_height = counts.max()

        # Title
        ax.set_title(f"{title} Apartment Area Distribution\nListings: {len(areas):,}", **self.styles["title"])

        # Axis labels
        ax.set_xlabel("Area (m²)", **self.styles["axis_title"])
        ax.set_ylabel("Count", **self.styles["axis_title"])

        # Styling
        self.style_axes(ax, fig, max_height)

        self.save_fig(fig, histogram_dir / f"area_{title.lower()}.png")

    def bedrooms_vs_price_boxplot_generate(self, df, title):
        """
        Generates boxplot of price by number of bedrooms.

        Parameters:
        - df: filtered dataframe (sale_df or rent_df)
        - title: "Sale" or "Rent"
        """
        boxplot_dir = self.inner_dir / "bedrooms_vs_price_boxplot"
        boxplot_dir.mkdir(parents=True, exist_ok=True)

        bedroom_groups = []
        bedroom_labels = []

        for bedrooms in range(1, 11):
            prices = df[df["bedrooms"] == bedrooms]["price"].values

            if len(prices) < 10:
                continue

            bedroom_groups.append(prices)
            bedroom_labels.append(str(int(bedrooms)))

        # Plot
        fig, ax = plt.subplots(figsize=self.figsize)
        boxplot = ax.boxplot(bedroom_groups, labels=bedroom_labels, showfliers=False, patch_artist=True)

        for patch in boxplot["boxes"]:
            patch.set_facecolor(self.transaction_colors.get(title, "#CCCCCC"))
            patch.set_alpha(0.6)

        # Title + subtitle
        ax.set_title(f"{title} Price by Number of Bedrooms\nListings: {len(df):,}", **self.styles["title"])

        # Axis labels
        ax.set_xlabel("Bedrooms", **self.styles["axis_title"])
        ax.set_ylabel("Price (USD)", **self.styles["axis_title"])

        # Styling
        max_height = max([max(group) for group in bedroom_groups])
        self.style_axes(ax, fig, max_height)

        self.save_fig(fig, boxplot_dir / f"{title.lower()}.png")

    def floor_distribution_bar_chart_generate(self):
        """
        Generates floor distribution bar charts (bucketed) per city.

        Parameters:
        - df: filtered dataframe (sale_df / rent_df / combined)
        - title: optional (e.g. "Sale", "Rent", or "All")
        """
        floor_dir = self.inner_dir / "floor_bar_charts"
        floor_dir.mkdir(parents=True, exist_ok=True)

        df = self.df.copy()

        # Floor bucket helper (local)
        def bucket_floor(floor):
            if floor <= 2:
                return "1–2"
            elif floor <= 5:
                return "3–5"
            elif floor <= 9:
                return "6–9"
            elif floor <= 15:
                return "10–15"
            else:
                return "16+"

        df["floor_bucket"] = df["floor"].apply(bucket_floor)
        bucket_order = ["1–2", "3–5", "6–9", "10–15", "16+"]

        for city in self.cities:
            city_df = df[df["city"] == city]
            counts = (city_df["floor_bucket"].value_counts().reindex(bucket_order, fill_value=0))
            fig, ax = plt.subplots(figsize=self.figsize)

            color = self.city_colors.get(city, "#CCCCCC")
            bars = ax.bar(counts.index, counts.values, color=color, alpha=0.8)

            max_height = counts.values.max()
            offset = self.bar_label_offset(max_height)

            # Labels
            for bar, value in zip(bars, counts.values):
                ax.text(bar.get_x() + bar.get_width() / 2, value + offset, f"{value:,}", **self.styles["bar_label"])

            english_city = self.CITY_MAP.get(city, city)

            # Title
            ax.set_title(f"Floor Distribution - {english_city}\n"f"Listings: {counts.sum():,}", **self.styles["title"])

            # Axis labels
            ax.set_xlabel("Floor Range", **self.styles["axis_title"])
            ax.set_ylabel("Count", **self.styles["axis_title"])

            # Styling
            self.style_axes(ax, fig, max_height)

            self.save_fig(fig, floor_dir / f"floor_{english_city.lower()}.png")

    def generate(self):
        # Area histograms
        self.area_distribution_histogram_generate(self.sale_df, "Sale")
        self.area_distribution_histogram_generate(self.rent_df, "Rent")

        # Bedrooms box plots
        self.bedrooms_vs_price_boxplot_generate(self.sale_df, "Sale")
        self.bedrooms_vs_price_boxplot_generate(self.rent_df, "Rent")

        # Floor Distribution
        self.floor_distribution_bar_chart_generate()
