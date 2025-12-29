from .ApartmentsDataFrame import ApartmentsDataFrame
from ..utils.helpers import get_usd_exchange_rate, geo_months
import pandas as pd
from datetime import datetime, timedelta



class DataCleaning:
    def __init__(self):
        self.apartments_df = ApartmentsDataFrame().get_df()
        self.currency_rate = get_usd_exchange_rate()

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
        """Clean area_m2 column by removing 'მ²' from strings and converting to numeric"""
        self.apartments_df['area_m2'] = self.apartments_df['area_m2'].apply(
            lambda x: x[:-2] if isinstance(x, str) and x.endswith('მ²') else x
        )
        self.apartments_df['area_m2'] = pd.to_numeric(self.apartments_df['area_m2'], errors='coerce')

    def __clean_and_transform_price(self):
        """ Removes the $ sign and converts to USD if in Georgian Lari or marks price as None if it's negotiable. """
        def parse_price(price):
            price_str = str(price).replace(',', '').strip().lower()

            try:
                if '$' in price_str:
                    return float(price_str.replace('$', '').strip())
                else:
                    if '₾' in price_str:
                        price_str = price_str.replace('₾', '').strip()
                    return round(float(price_str) * self.currency_rate)
            except ValueError:
                return None
        self.apartments_df['price'] = self.apartments_df['price'].apply(parse_price)

    def __clean_price_per_sqm(self):
        def clean_row(row):
            if pd.isna(row['price_per_sqm']):
                try:
                    return int(row['price']) // int(row['area_m2'])
                except (TypeError, ZeroDivisionError):
                    return None

            value = str(row['price_per_sqm']).strip()
            if '/' in value:
                value = value.split('/')[0].strip()

            if '$' in value:
                value = value.replace('$', '').replace(',', '').strip()
                return float(value)
            else:
                value = value.replace(',', '').strip()
                return round(float(value) * self.currency_rate)

        self.apartments_df['price_per_sqm'] = self.apartments_df.apply(clean_row, axis=1)

    def __fill_district_name_nulls(self):
        """Fills missing values in the district_name column with a default message."""
        self.apartments_df['district_name'] = self.apartments_df['district_name'].fillna(pd.NA)
        print("NULL COLUMNS IN DISTRICT_NAME COLUMN HAVE BEEN FILLED")

    def __transform_bedrooms(self):
        """Cleans raw bedroom values, extracts numeric info from strings like 'საძ. 3',
        and fills nulls using area as a heuristic."""

        def extract_bedroom_number(val):
            if isinstance(val, str) and 'საძ' in val:
                parts = val.strip().split()
                if len(parts) > 1 and parts[1].isdigit():
                    return int(parts[1])

            elif not pd.isna(val):
                return int(val)
            return pd.NA

        def infer_bedrooms(area):
            if area is None or pd.isna(area):
                return pd.NA
            elif area <= 50:
                return 1
            elif area <= 100:
                return 2
            elif area <= 150:
                return 3
            else:
                return 4

        self.apartments_df['bedrooms'] = self.apartments_df['bedrooms'].apply(extract_bedroom_number)
        self.apartments_df['bedrooms'] = self.apartments_df.apply(
            lambda row: infer_bedrooms(row['area_m2']) if pd.isna(row['bedrooms']) else row['bedrooms'],
            axis=1
        )
        self.apartments_df['bedrooms'] = self.apartments_df['bedrooms'].astype('Int64')

        print("Transformed and filled missing 'bedrooms' column.")

    def __transform_floor(self):
        """Cleans raw floor values, extracts numeric info from strings like 'სართ. 3' or '8/11', and fills nulls."""

        def extract_floor_number(val):
            if pd.isna(val) or val is None:
                return pd.NA

            if isinstance(val, str):
                val = val.strip()
                if 'სართ' in val:
                    parts = val.split()
                    if len(parts) > 1 and parts[1].isdigit():
                        return int(parts[1])
                elif '/' in val and '-' not in val:
                    parts = val.split('/')
                    if len(parts) > 0 and parts[0].isdigit():
                        return int(parts[0])
                elif val.isdigit():
                    return int(val)
                else:
                    return pd.NA

            elif isinstance(val, (int, float)):
                return int(val)

            return pd.NA

        self.apartments_df['floor'] = self.apartments_df['floor'].apply(extract_floor_number)
        self.apartments_df['floor'] = self.apartments_df['floor'].astype('Int64')

    def __transform_upload_date(self):
        df = self.apartments_df.copy()
        df['upload_date'] = df['upload_date'].astype(str)
        now = datetime.now()

        def parse_date(upload_str):
            try:
                parts = upload_str.split()
                if len(parts) != 3:
                    return pd.NA

                if 'წუთი' in upload_str:
                    # Example input: '25 წუთის წინ'
                    new_time = now - timedelta(minutes=int(parts[0]))
                    return new_time.strftime("%Y-%m-%d %H:%M")
                elif 'საათი' in upload_str:
                    # Example input: '13 საათის წინ'
                    new_time = now - timedelta(hours=int(parts[0]))
                    return new_time.strftime("%Y-%m-%d %H:%M")
                elif ':' in upload_str:
                    # Example input: '09 ივლ 16:20'
                    day, geo_month_abbr, time_str = [p.strip() for p in parts]
                    month = geo_months.get(geo_month_abbr[:3])
                    if not month:
                        return None
                    return datetime(year=now.year, month=month, day=int(day), hour=int(time_str[:2]),
                                    minute=int(time_str[3:5])).strftime("%Y-%m-%d %H:%M")
                else:
                    # Example input: "09 ივლ 2025"
                    day, geo_month_abbr, year = [p.strip() for p in parts]
                    month = geo_months.get(geo_month_abbr[:3])
                    return (datetime(year=int(year), month=month, day=int(day), hour=12, minute=0)
                            .strftime("%Y-%m-%d %H:%M"))
            except:
                return None

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

    def write_to_csv(self, path="../data_output/cleaned_apartments.csv"):
        """ Writes the dataset to a csv file. """
        self.apartments_df.to_csv(path, index=False, na_rep='<NA>')

    def main(self):
        self.__get_shape()
        self.__get_info()
        self.__get_description()
        self.__get_null_columns()

        self.__clean_and_transform_price()
        self.__clean_area_m2()
        self.__clean_price_per_sqm()

        self.__transform_bedrooms()
        self.__transform_floor()

        self.__transform_upload_date()
        self.__new_transaction_type_col()

        self.__fill_district_name_nulls()
