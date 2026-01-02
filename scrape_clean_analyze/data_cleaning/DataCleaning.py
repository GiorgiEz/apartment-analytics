from ..utils.helpers import get_usd_exchange_rate, geo_months
import pandas as pd
from datetime import datetime, timedelta



class DataCleaning:
    def __init__(self, apartments_df, currency_rate=None):
        self.apartments_df = apartments_df
        self.currency_rate = currency_rate or get_usd_exchange_rate()

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

    def _clean_area_m2(self):
        """
        Clean area_m2 column by extracting numeric values and converting to nullable numeric type.
        Handles:
        - "50 მ²", "45 მ2", "60"
        - extra spaces
        - invalid / missing values -> pd.NA
        """
        self.apartments_df['area_m2'] = (
            self.apartments_df['area_m2']
            .astype(str)
            .str.extract(r'(\d+(?:\.\d+)?)')[0]
            .astype('Float64')
        )

    def _clean_and_transform_price(self):
        """
        Cleans price column:
        - USD: "$100,000", "100000$", "100,000 $" -> 100000
        - GEL: "103,808", "103,808 ₾", "103808" -> converted to USD
        - Invalid / negotiable / missing -> pd.NA
        """

        def parse_price(value):
            if pd.isna(value):
                return pd.NA

            price_str = str(value).lower().replace(',', '').strip()

            try:
                # USD
                if '$' in price_str:
                    number = price_str.replace('$', '').strip()
                    return float(number)

                # GEL (explicit symbol or implicit)
                number = price_str.replace('₾', '').strip()
                return float(number) * self.currency_rate

            except ValueError:
                return pd.NA

        self.apartments_df['price'] = (
            self.apartments_df['price']
            .apply(parse_price)
            .astype('Float64')
        )

    def _clean_price_per_sqm(self):
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

    def _transform_bedrooms(self):
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

    def _transform_floor(self):
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

    def _transform_upload_date(self):
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

    def _new_transaction_type_col(self):
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
        if self.apartments_df.empty:
            print(f"No data to write After Performing Data Cleaning")
            return
        self.apartments_df.to_csv(path, index=False, na_rep='<NA>')

    def main(self):
        self.__get_shape()
        self.__get_info()
        self.__get_description()
        self.__get_null_columns()

        self._clean_and_transform_price()
        self._clean_area_m2()
        self._clean_price_per_sqm()

        self._transform_bedrooms()
        self._transform_floor()

        self._transform_upload_date()
        self._new_transaction_type_col()
