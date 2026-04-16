from data_analysis.EDA.DataAnalysis import DataAnalysis
import matplotlib.pyplot as plt
import pandas as pd



class TimeAnalysis(DataAnalysis):
    """ Time Analysis class used to generate listings count and median price and price per sqm line charts """
    def __init__(self, sale_df, rent_df, combined_df):
        super().__init__()
        self.inner_dir = self.output_dir / "time_analysis"
        self.inner_dir.mkdir(parents=True, exist_ok=True)
        self.sale_df = sale_df
        self.rent_df = rent_df
        self.df = combined_df

    def listings_over_time_generate(self):
        """ Generates monthly listings trend chart: - Sale vs Rent comparison """

        def prepare_monthly_counts(df):
            df = df[df["upload_date"].notna()].copy()

            df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")
            df = df.dropna(subset=["upload_date"])

            if df.empty:
                return None

            df["year_month"] = df["upload_date"].dt.to_period("M")

            counts = df.groupby("year_month").size().sort_index()

            if counts.empty:
                return None

            counts.index = counts.index.to_timestamp()
            return counts

        # Prepare data
        sale_counts = prepare_monthly_counts(self.sale_df)
        rent_counts = prepare_monthly_counts(self.rent_df)

        if sale_counts is None and rent_counts is None:
            return

        fig, ax = plt.subplots(figsize=self.figsize)

        # SALE
        if sale_counts is not None:
            ax.plot(sale_counts.index, sale_counts.values, marker="o", linewidth=2,
                label=f"Sale ({sale_counts.sum():,})", color=self.transaction_colors["Sale"]
            )

        # RENT
        if rent_counts is not None:
            ax.plot(rent_counts.index, rent_counts.values, marker="o", linewidth=2,
                label=f"Rent ({rent_counts.sum():,})", color=self.transaction_colors["Rent"]
            )

        # Titles
        total_listings = (sale_counts.sum() if sale_counts is not None else 0) + \
                         (rent_counts.sum() if rent_counts is not None else 0)

        ax.set_title(f"Listings Over Time\nTotal Listings: {total_listings:,}", **self.styles["title"])

        ax.set_xlabel("Month", **self.styles["axis_title"])
        ax.set_ylabel("Number of Listings", **self.styles["axis_title"])

        # Styling
        self.style_axes(ax)

        ax.legend()
        fig.autofmt_xdate()

        self.save_fig(fig, self.inner_dir / "listings_over_time.png")

    def median_feature_over_time_by_city_generate(self, df, title, feature):
        """
        Generates monthly median trend line chart for a given feature (price or price_per_sqm),
        with separate lines for each city.

        Parameters:
        - df: dataframe (sale_df or rent_df)
        - title: string (Sale or Rent)
        - feature: "price" or "price_per_sqm"
        """

        time_dir = self.inner_dir / "price_trend"
        time_dir.mkdir(parents=True, exist_ok=True)

        # Basic cleaning
        df = df[df["upload_date"].notna() & df["city"].notna() & df[feature].notna() & (df[feature] > 0)].copy()

        df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")
        df = df.dropna(subset=["upload_date"])

        if df.empty:
            return

        # Create month column
        df["year_month"] = df["upload_date"].dt.to_period("M")

        fig, ax = plt.subplots(figsize=self.figsize)

        # Track if anything is plotted
        plotted = False

        for city in self.cities:
            city_df = df[df["city"] == city]

            if len(city_df) < 20:
                continue

            # Group by month → median
            monthly_median = (city_df.groupby("year_month")[feature].median().sort_index())

            if monthly_median.empty:
                continue

            # Convert index
            monthly_median.index = monthly_median.index.to_timestamp()

            # Plot
            ax.plot(monthly_median.index, monthly_median.values, marker="o", linewidth=2,
                label=f"{self.CITY_MAP.get(city, city)} ({len(city_df):,})", color=self.city_colors.get(city, "#CCCCCC")
            )

            plotted = True

        if not plotted:
            return

        # Title
        feature_label = "Price" if feature == "price" else "Price per m²"

        ax.set_title(f"{title} Median {feature_label} Over Time by City\nListings: {len(df):,}", **self.styles["title"])

        ax.set_xlabel("Month", **self.styles["axis_title"])
        ax.set_ylabel(f"{feature_label} (USD)", **self.styles["axis_title"])

        # Styling
        self.style_axes(ax)

        ax.legend()
        fig.autofmt_xdate()

        self.save_fig(fig, time_dir / f"{title.lower()}_{feature}_over_time.png")

    def generate(self):
        # Listings over time
        self.listings_over_time_generate()

        # Median price and price per sqm comparisons
        self.median_feature_over_time_by_city_generate(self.sale_df, "Sale", "price_per_sqm")
        self.median_feature_over_time_by_city_generate(self.rent_df, "Rent", "price")
