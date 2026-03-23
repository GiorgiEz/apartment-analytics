import pandas as pd



class Preprocessing:
    def __init__(self, sale_train, rent_train, sale_test, rent_test):
        self.sale_train = sale_train.copy()
        self.sale_test = sale_test.copy()

        self.rent_train = rent_train.copy()
        self.rent_test = rent_test.copy()

    def _apply_to_all(self, func):
        """ Helper function that applies the given function to all dataframes """
        for df_attr in ["sale_train", "rent_train", "sale_test", "rent_test"]:
            setattr(self, df_attr, func(getattr(self, df_attr)))

    def get_dfs(self):
        return self.sale_train, self.sale_test, self.rent_train, self.rent_test

    def __remove_missing_rows(self):
        """ Removes rows with missing values for the following columns """
        self._apply_to_all(lambda df: df.dropna(subset=["price", "area_m2", "district_name", "upload_date", "floor"]))

    def __remove_extreme_areas(self):
        """ Removes area_m2 values that are too high or low"""
        self._apply_to_all(lambda df: df[(df["area_m2"] >= 20) & (df["area_m2"] <= 500)])

    def __remove_extreme_bedrooms(self):
        """ Removes bedrooms values that are too high or low"""
        self._apply_to_all(lambda df: df[(df["bedrooms"] > 0) & (df["bedrooms"] <= 10)])

    def __remove_extreme_floors(self):
        """ Removes floor values that are too high or low"""
        self._apply_to_all(lambda df: df[(df["floor"] > 0) & (df["floor"] <= 60)])

    def __check_logical_relationships(self):
        # Removes row if there is impossible relationship between Area and bedrooms
        self._apply_to_all(lambda df: df[(df["bedrooms"] == 0) | (df["area_m2"] / df["bedrooms"] >= 15)])

    def __remove_extreme_price_per_sqm(self):
        sale_lower = self.sale_train["price_per_sqm"].quantile(0.02)
        sale_upper = self.sale_train["price_per_sqm"].quantile(0.99)

        rent_lower = self.rent_train["price_per_sqm"].quantile(0.02)
        rent_upper = self.rent_train["price_per_sqm"].quantile(0.99)

        # Removes too low or too high price_per_sqm values
        self.sale_train = self.sale_train[(self.sale_train["price_per_sqm"] > sale_lower) & (self.sale_train["price_per_sqm"] < sale_upper)]
        self.sale_test = self.sale_test[(self.sale_test["price_per_sqm"] > sale_lower) & (self.sale_test["price_per_sqm"] < sale_upper)]
        self.rent_train = self.rent_train[(self.rent_train["price_per_sqm"] > rent_lower) & (self.rent_train["price_per_sqm"] < rent_upper)]
        self.rent_test = self.rent_test[(self.rent_test["price_per_sqm"] > rent_lower) & (self.rent_test["price_per_sqm"] < rent_upper)]

    def __remove_extreme_prices(self):
        """ Removes extreme price values for sale and monthly rent apartments """

        def clean_prices(train, test):
            price_col = "price"

            # compute bounds from train
            grp = train.groupby(["city", "district_name"])[price_col]

            bounds = grp.quantile([0.25, 0.75]).unstack()
            bounds.columns = ["q1", "q3"]

            bounds["iqr"] = bounds["q3"] - bounds["q1"]
            bounds["lower"] = bounds["q1"] - 1.5 * bounds["iqr"]
            bounds["upper"] = bounds["q3"] + 1.5 * bounds["iqr"]

            bounds = bounds.reset_index()

            # apply to train
            train = train.merge(bounds, on=["city", "district_name"], how="left")
            train = train[(train[price_col] >= train["lower"]) & (train[price_col] <= train["upper"])]
            train = train.drop(columns=["q1", "q3", "iqr", "lower", "upper"])

            # apply to test
            test = test.merge(bounds, on=["city", "district_name"], how="left")
            test = test[(test[price_col] >= test["lower"]) & (test[price_col] <= test["upper"])]
            test = test.drop(columns=["q1", "q3", "iqr", "lower", "upper"])

            return train, test

        self.sale_train, self.sale_test = clean_prices(self.sale_train, self.sale_test)
        self.rent_train, self.rent_test = clean_prices(self.rent_train, self.rent_test)

    def __extract_year_and_month(self):
        """Extract year and month, normalize year using train minimum"""

        def extract(df, min_year):
            df["upload_date"] = pd.to_datetime(df["upload_date"], errors="coerce")

            df["upload_year"] = df["upload_date"].dt.year - min_year
            df["upload_month"] = df["upload_date"].dt.month

        # compute rule from train
        sale_min_year = pd.to_datetime(self.sale_train["upload_date"], errors='coerce').dt.year.min()
        rent_min_year = pd.to_datetime(self.rent_train["upload_date"], errors='coerce').dt.year.min()

        # apply to train
        extract(self.sale_train, sale_min_year)
        extract(self.rent_train, rent_min_year)

        # apply same rule to test
        extract(self.sale_test, sale_min_year)
        extract(self.rent_test, rent_min_year)

    def run(self):
        """ Main method to run Preprocessing tasks before model training """
        self.__remove_missing_rows()

        self.__remove_extreme_areas()
        self.__remove_extreme_bedrooms()
        self.__remove_extreme_floors()

        self.__check_logical_relationships()

        self.__remove_extreme_price_per_sqm()
        self.__remove_extreme_prices()

        self.__extract_year_and_month()
