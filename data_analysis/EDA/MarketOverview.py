import matplotlib.pyplot as plt
from data_analysis.EDA.DataAnalysis import DataAnalysis



class MarketOverview(DataAnalysis):
    """ Market Overview class, used to generate city listing distributions and transaction type comparisons """
    def __init__(self, sale_df, rent_df, combined_df):
        super().__init__()
        self.inner_dir = self.output_dir / "market_overview"
        self.inner_dir.mkdir(parents=True, exist_ok=True)
        self.sale_df = sale_df
        self.rent_df = rent_df
        self.df = combined_df

    def __city_distribution_generate(self):
        """
        Generates a bar chart showing the distribution of apartment listings by city.
        Displays each city's percentage share and total listing count, providing
        a high-level overview of market concentration and geographic composition.
        """
        city_counts = self.df["city"].value_counts()
        total = city_counts.sum()
        colors = [self.city_colors.get(city, "#CCCCCC") for city in city_counts.index]

        fig, ax = plt.subplots(figsize=self.figsize)

        city_names = [self.CITY_MAP.get(city, city) for city in city_counts.index]
        bars = ax.bar(city_names, city_counts.values, color=colors)  # Bar chart

        max_height = city_counts.values.max()
        offset = self.bar_label_offset(max_height)

        # Add annotations (percentage + count)
        for i, bar in enumerate(bars):
            height = bar.get_height()
            pct = (height / total) * 100
            text_pos = bar.get_x() + bar.get_width() / 2

            ax.text(text_pos, height + offset, f"{pct:.1f}%\n({int(height)})", **self.styles["bar_label"])

        ax.set_title(f"Apartment Distribution by City\nTotal listings: {total:,}", **self.styles["title"])  # Title

        # X and Y labels
        ax.set_xlabel("City", **self.styles["axis_title"])
        ax.set_ylabel("Number of Listings", **self.styles["axis_title"])

        self.style_axes(ax, fig, max_height)  # Other Styles

        self.save_fig(fig, self.inner_dir / "city_distribution.png")

    def __transaction_distribution_generate(self):
        """ Generate a pie chart showing the distribution of different transaction types """
        values = [len(self.sale_df), len(self.rent_df)]
        total = sum(values)

        fig, ax = plt.subplots(figsize=self.figsize)

        # Pie chart
        ax.pie(
            values,
            labels=["Sale", "Rent"],
            autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct / 100 * total))})",
            startangle=90,
            colors=[self.transaction_colors["Sale"], self.transaction_colors["Rent"]],
            explode=[0.03, 0.03],
            textprops=self.styles["pie_textprops"],
        )

        ax.set_title(f"Transaction Type Distribution\nTotal listings: {total:,}", **self.styles["title"])
        ax.axis("equal")

        self.save_fig(fig, self.inner_dir / "transaction_distribution.png")

    def __transaction_by_city_generate(self):
        """ Generate a pie chart showing the distribution of different transaction types per each city """
        # Group counts per (city, transaction_type)
        sale_grouped = self.sale_df.groupby(["city"]).size()
        rent_grouped = self.rent_df.groupby(["city"]).size()

        for city in self.cities:
            values = [sale_grouped.loc[city], rent_grouped.loc[city]]
            total = sum(values)

            fig, ax = plt.subplots(figsize=self.figsize)
            city_color = self.city_colors.get(city, "#CCCCCC")

            ax.pie(
                values,
                labels=["Sale", "Rent"],
                autopct=lambda pct: f"{pct:.1f}%\n({int(round(pct / 100 * total))})",
                startangle=90,
                colors=[self.lighten_color(city_color, 0.2), self.lighten_color(city_color, 0.6)],
                explode=[0.03, 0.03],
                textprops=self.styles["pie_textprops"],
            )

            city_name = self.CITY_MAP.get(city, city)
            ax.set_title(f"{city_name} — Transaction Distribution\nTotal: {total:,}", **self.styles["title"])
            ax.axis("equal")

            self.save_fig(fig, self.inner_dir / f"transaction_by_{city_name.lower()}.png")  # Save per city

    def generate(self):
        self.__city_distribution_generate()
        self.__transaction_distribution_generate()
        self.__transaction_by_city_generate()
