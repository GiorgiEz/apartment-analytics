from .ApartmentsDataFrame import ApartmentsDataFrame
import pandas as pd
from datetime import datetime



class DataCleaning:
    def __init__(self):
        self.apartments_df = ApartmentsDataFrame().get_df()

    def __get_shape(self):
        """ Prints the shape of the dataset. Useful for quickly understanding the size of the dataset. """
        print("SHAPE OF THE APARTMENTS DATASET: ", self.apartments_df.shape)

    def __get_info(self):
        """ Prints detailed information about the dataset. Helpful for understanding the dataset structure. """
        print("THE APARTMENTS DATASET INFORMATION: ", self.apartments_df.info(), '\n')

    def __get_description(self):
        """ Prints a statistical summary of the dataset. Useful for a quick overview of data distribution. """
        print("DESCRIPTION OF THE APARTMENTS DATASET:\n", self.apartments_df.describe(), '\n')

    def __get_null_columns(self):
        """ Prints the count of missing (null) values for each column in the dataset. """
        print("AMOUNT OF NULL VALUES IN APARTMENTS DATASET: \n", self.apartments_df.isnull().sum(), '\n')

    def __clean_area_m2(self):
        """ Remove 'მ²' from area_m2 column and convert it to numeric value """
        self.apartments_df['area_m2'] = self.apartments_df['area_m2'].str[:-2]
        self.apartments_df['area_m2'] = pd.to_numeric(self.apartments_df['area_m2'], errors='coerce')

    def __clean_price_per_sqm(self):
        """ Remove '/ მ²' from price_per_sqm column and convert it to numeric value """
        self.apartments_df['price_per_sqm'] = (
            self.apartments_df['price_per_sqm']
            .astype(str)
            .str.replace(",", "")  # remove commas
            .str.extract(r'(\d+)')  # extract the number part
        )
        self.apartments_df['price_per_sqm'] = pd.to_numeric(self.apartments_df['price_per_sqm'], errors='coerce')

    def __fill_price_per_sqm_nulls(self):
        """ Fills the missing values in the price_per_sqm column with price / area_m2. """
        # Convert columns to numeric in case they're strings (safe conversion)
        df = self.apartments_df.copy()
        df['price'] = df['price'].astype(str).str.replace(",", "")
        df['price'] = pd.to_numeric(df['price'], errors='coerce')

        # Compute price_per_sqm only where it's null and area_m2 is not zero
        mask = df['price_per_sqm'].isna() & df['area_m2'].notna() & (df['area_m2'] != 0)
        df.loc[mask, 'price_per_sqm'] = df.loc[mask, 'price'] // df.loc[mask, 'area_m2']

        self.apartments_df = df
        print("NULL COLUMNS IN PRICE_PER_SQM COLUMN HAS BEEN FILLED")

    def __fill_street_name_nulls(self):
        """Fills missing values in the street_name column with a default message."""
        self.apartments_df['street_name'] = self.apartments_df['street_name'].fillna("არ არის მოწოდებული")
        print("NULL COLUMNS IN STREET_NAME COLUMN HAVE BEEN FILLED")

    def __transform_upload_date(self):
        # Georgian abbreviated month names to numbers
        geo_months = {
            'იან': 1, 'თებ': 2, 'მარ': 3, 'აპრ': 4, 'მაი': 5, 'ივნ': 6,
            'ივლ': 7, 'აგვ': 8, 'სექ': 9, 'ოქტ': 10, 'ნოე': 11, 'დეკ': 12
        }

        # Ensure the column is string
        df = self.apartments_df.copy()
        df['upload_date'] = df['upload_date'].astype(str)

        def parse_date(upload_str):
            try:
                parts = upload_str.split()
                if len(parts) != 3:
                    return None
                day, geo_month_abbr, time_str = parts
                month = geo_months.get(geo_month_abbr[:3])
                if not month:
                    return None
                now = datetime.now()
                return datetime(year=now.year, month=month, day=int(day), hour=int(time_str[:2]),
                                minute=int(time_str[3:5]))
            except:
                return None

        # Apply to column
        df['upload_date'] = df['upload_date'].apply(parse_date)
        self.apartments_df = df

    def __new_transaction_type_col(self):
        """Extracts the transaction type from description and creates a new column."""

        def extract_transaction_type(desc):
            if not isinstance(desc, str):
                return None
            desc = desc.strip()
            if "იყიდება" in desc:
                return "იყიდება"
            elif "გირავდება" in desc:
                return "გირავდება"
            elif "ქირავდება დღიურად" in desc:
                return "ქირავდება დღიურად"
            elif "ქირავდება" in desc:
                return "ქირავდება თვიურად"
            else:
                return None

        self.apartments_df['transaction_type'] = self.apartments_df['description'].apply(extract_transaction_type)
        print("New column 'transaction_type' has been created based on descriptions.")

    def write_to_csv(self, path):
        """ Writes the dataset to a csv file. """
        self.apartments_df.to_csv(path, index=False)

    def main(self):
        self.__get_shape()
        self.__get_info()
        self.__get_description()
        self.__get_null_columns()

        self.__clean_area_m2()
        self.__clean_price_per_sqm()

        self.__transform_upload_date()
        self.__new_transaction_type_col()

        self.__fill_price_per_sqm_nulls()
        self.__fill_street_name_nulls()
        self.__get_null_columns()
