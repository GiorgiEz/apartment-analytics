


class Preprocessing:
    def __init__(self, train_df, validation_df, test_df, transaction_type):
        self.train_df = train_df
        self.validation_df = validation_df
        self.test_df = test_df
        self.transaction_type = transaction_type

    def get_dataframes(self):
        return self.train_df, self.validation_df, self.test_df

    def _apply_to_all(self, func):
        """ Helper function that applies the given function to all dataframes """
        for df_attr in ["train_df", "validation_df", "test_df"]:
            df = getattr(self, df_attr)
            df = func(df.copy())
            setattr(self, df_attr, df)

    def _remove_missing_rows(self):
        """ Removes rows with missing values for the following columns """
        self._apply_to_all(lambda df: df.dropna(subset=["price", "area_m2", "district_name", "upload_date", "floor"]))

    def _recalculate_price_per_sqm(self):
        self._apply_to_all(
            lambda df: df.assign(price_per_sqm=round(df["price"] / df["area_m2"], 2))
        )

    def _remove_extreme_areas(self):
        """ Removes area_m2 values that are too high or low"""
        self._apply_to_all(lambda df: df[(df["area_m2"] >= 15) & (df["area_m2"] <= 500)])

    def _remove_extreme_bedrooms(self):
        """ Removes bedrooms values that are too high or low"""
        self._apply_to_all(lambda df: df[(df["bedrooms"] > 0) & (df["bedrooms"] <= 10)])

    def _remove_extreme_floors(self):
        """ Removes floor values that are too high or low"""
        self._apply_to_all(lambda df: df[(df["floor"] > 0) & (df["floor"] <= 60)])

    def _remove_extreme_price_per_sqm(self):
        # 1. Global Quantile Filtering
        train_lower = self.train_df["price_per_sqm"].quantile(0.02)
        train_upper = self.train_df["price_per_sqm"].quantile(0.99)

        # Removes too low or too high price_per_sqm values
        self._apply_to_all(
            lambda df: df[(df["price_per_sqm"] >= train_lower) & (df["price_per_sqm"] <= train_upper)]
        )

        # 2. Local IQR filter per city and district
        price_col = "price_per_sqm"
        grp = self.train_df.groupby(["city", "district_name"])[price_col] # compute bounds from train

        bounds = grp.quantile([0.25, 0.75]).unstack()
        bounds.columns = ["q1", "q3"]

        bounds["iqr"] = bounds["q3"] - bounds["q1"]
        bounds["lower"] = bounds["q1"] - 1.5 * bounds["iqr"]
        bounds["upper"] = bounds["q3"] + 1.5 * bounds["iqr"]

        bounds = bounds.reset_index()

        def apply_filter(df):
            df = df.merge(bounds, on=["city", "district_name"], how="left")

            # fallback for unseen districts
            df["lower"] = df["lower"].fillna(df[price_col])
            df["upper"] = df["upper"].fillna(df[price_col])

            df = df[(df[price_col] >= df["lower"]) & (df[price_col] <= df["upper"])]

            return df.drop(columns=["q1", "q3", "iqr", "lower", "upper"])

        self.train_df = apply_filter(self.train_df)
        self.validation_df = apply_filter(self.validation_df)
        self.test_df = apply_filter(self.test_df)

        # 3. Strict manual filtering
        if self.transaction_type == "Sale":
            self._apply_to_all(
                lambda df: df[(df["price_per_sqm"] >= 150) & (df["price_per_sqm"] <= 10000)]
            )
        elif self.transaction_type == "Rent":
            self._apply_to_all(
                lambda df: df[(df["price_per_sqm"] >= 2) & (df["price_per_sqm"] <= 100)]
            )

    def run(self):
        """ Main method to run Preprocessing tasks before model training """
        self._remove_missing_rows()

        self._remove_extreme_areas()
        self._remove_extreme_bedrooms()
        self._remove_extreme_floors()

        self._recalculate_price_per_sqm()
        self._remove_extreme_price_per_sqm()
