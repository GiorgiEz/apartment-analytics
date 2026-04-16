class Preprocessing:
    """ Soft preprocessing before Exploratory Data Analysis is performed """
    def __init__(self, df):
        self.df = df

    def __deduplicate(self):
        """ Deduplicates based on price, area, city, district, street, floor and bedrooms.
            If these features are exactly the same across different rows than the last one is kept.
        """
        self.df = (
            self.df.sort_values("upload_date")
            .drop_duplicates(
                subset=["price", "area_m2", "city", "district_name", "street_address", "floor", "bedrooms"],
                keep="last"
            )
        )

    def __filter_by_city(self):
        """ Groups prices by city and uses 0.01 and 0.995 quantiles as lower and upper bounds. """
        grouped = self.df.groupby("city")["price"]

        bounds = grouped.quantile([0.01, 0.995]).unstack()
        bounds.columns = ["lower", "upper"]
        bounds = bounds.reset_index()

        df = self.df.merge(bounds, on="city", how="left")

        df = df[(df["price"] >= df["lower"]) & (df["price"] <= df["upper"])]

        df.drop(columns=["lower", "upper"])

        self.df = df

    def __soft_filtering(self):
        """ General soft filtering, dropping null values, filtering area, floor, bedrooms, price and price per sqm"""
        df = self.df.copy()

        # basic cleaning
        df = df.dropna(subset=["price", "area_m2"])

        # area filtering
        df = df[(df["area_m2"] >= 15) & (df["area_m2"] <= 700)]

        # floor filtering
        df = df[df["floor"] < 60]

        # bedrooms filtering
        df = df[(df["bedrooms"] > 0) & (df["bedrooms"] <= 10)]

        # price filtering
        price_lower, price_upper = df["price"].quantile(0.01), df["price"].quantile(0.995)
        df = df[(df["price"] >= price_lower) & (df["price"] <= price_upper)]

        # price per sqm filtering
        price_per_sqm_lower, price_per_sqm_upper = df["price_per_sqm"].quantile(0.01), df["price_per_sqm"].quantile(0.995)
        df = df[(df["price_per_sqm"] >= price_per_sqm_lower) & (df["price_per_sqm"] <= price_per_sqm_upper)]

        self.df = df

    def run(self):
        """ Main function called from outside to run the preprocessing """
        # print(f'Before Preprocessing: {len(self.df)}')
        self.__deduplicate()
        self.__soft_filtering()
        self.__filter_by_city()
        # print(f'After Preprocessing: {len(self.df)}')
        return self.df
