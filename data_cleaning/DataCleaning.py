import re
import pandas as pd
from data_cleaning.NormalizeDistricts import NormalizeDistricts
from data_cleaning.utils.get_usd_exchange_rate import get_usd_exchange_rate
from datetime import datetime, timedelta
from config import paths



class DataCleaning:
    def __init__(self, apartments_df, currency_rate=None):
        self.apartments_df = apartments_df
        self.currency_rate = currency_rate or get_usd_exchange_rate()
        self.geo_months = {
            'იან': 1, 'თებ': 2, 'მარ': 3, 'აპრ': 4, 'მაი': 5, 'ივნ': 6,
            'ივლ': 7, 'აგვ': 8, 'სექ': 9, 'ოქტ': 10, 'ნოე': 11, 'დეკ': 12
        }

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

    def _normalize_price(self):
        """
        Cleans price column:

        Rules:
        - USD: value must contain '$' and be > 0 → kept as USD
        - GEL: value must contain '₾' and be > 0 → converted to USD
        - Zero / invalid / missing → pd.NA
        """

        def parse_price(value):
            if pd.isna(value):
                return pd.NA

            price_str = str(value).lower().replace(",", "").strip()

            try:
                # USD
                if "$" in price_str:
                    number = round(float(price_str.replace("$", "").strip()), 2)
                    return number if number > 0 else pd.NA

                # GEL
                if "₾" in price_str:
                    number = round(float(price_str.replace("₾", "").strip()), )
                    return round(number * self.currency_rate, 2) if number > 0 else pd.NA

                # No currency symbol -> keep as-is
                return round(float(price_str), 2) if round(float(price_str), 2) > 0 else pd.NA

            except ValueError:
                return pd.NA

        self.apartments_df["price"] = (self.apartments_df["price"].apply(parse_price).astype("Float64"))

    def _normalize_area_m2(self):
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

    def _normalize_price_per_sqm(self):
        """
        Cleans price_per_sqm column.

        Rules:
        - '$' present → USD, extracted as-is if > 0
        - '₾' present → GEL, converted to USD using currency_rate if > 0
        - No currency symbol → extracted number as-is if > 0
        - 0 / invalid → pd.NA
        - Missing → computed from price / area_m2
        """

        def parse_row(row):
            value = row.get("price_per_sqm")

            # Try to parse price_per_sqm directly
            if pd.notna(value):
                text = str(value).lower().replace(",", "").strip()

                match = re.search(r"\d+(?:\.\d+)?", text)
                if match:
                    amount = round(float(match.group()), 2)

                    if amount <= 0:
                        return pd.NA

                    # USD
                    if "$" in text:
                        return amount

                    # GEL
                    if "₾" in text:
                        return round(amount * self.currency_rate, 2)

                    # No currency symbol = "$" → keep as-is
                    return amount

            # Fallback: compute from price and area
            price = row.get("price")
            area = row.get("area_m2")

            if pd.notna(price) and pd.notna(area) and area > 0:
                value = round(float(price) / float(area), 2)
                return value if value > 0 else pd.NA

            return pd.NA

        self.apartments_df["price_per_sqm"] = (self.apartments_df.apply(parse_row, axis=1).astype("Float64"))

    def _normalize_bedrooms(self):
        """ Normalizes bedrooms column.
            Handles:"საძ. 1", "საძ1", "2". missing / invalid values → inferred from area_m2
        """

        def extract_bedrooms(value):
            if pd.isna(value):
                return pd.NA

            text = str(value).lower()

            match = re.search(r'\d+', text)
            if match:
                return int(match.group())

            return pd.NA

        def infer_bedrooms(area):
            if pd.isna(area):
                return pd.NA

            if area <= 50:
                return 1
            elif area <= 100:
                return 2
            elif area <= 150:
                return 3
            elif area <= 175:
                return 4
            elif area <= 200:
                return 5
            elif area <= 225:
                return 6
            else:
                return 7

        # extract explicit bedroom values
        self.apartments_df['bedrooms'] = self.apartments_df['bedrooms'].apply(extract_bedrooms).astype('Int64')

        # infer missing bedrooms from area
        self.apartments_df['bedrooms'] = self.apartments_df.apply(
            lambda row: (
                infer_bedrooms(row['area_m2'])
                if pd.isna(row['bedrooms'])
                else row['bedrooms']
            ),
            axis=1
        ).astype('Int64')

    def _normalize_floor(self):
        """ Normalizes floor column.
            Handles: "სართ. 3", "8/11", "5". missing / invalid values → pd.NA
        """

        def extract_floor(value):
            if pd.isna(value):
                return pd.NA

            text = str(value)
            match = re.search(r'\d+', text)
            if match:
                return int(match.group())

            return pd.NA

        self.apartments_df['floor'] = self.apartments_df['floor'].apply(extract_floor).astype('Int64')

    def _normalize_upload_date(self, now=None):
        """ Normalizes upload_date column.
            Handles: "1 წუთის წინ", "23 საათის წინ", "30 დეკ, 12:02", "02 იან 12:44", "01 იან 2026"
        """

        now = now or datetime.now()

        def parse_date(value):
            if pd.isna(value):
                return pd.NA

            # Already-normalized datetime (string or datetime)
            parsed = pd.to_datetime(value, errors="coerce")
            if pd.notna(parsed):
                if parsed <= now:
                    return parsed.floor("min")
                else:
                    # future timestamps are invalid → roll back one year
                    return parsed.replace(year=parsed.year - 1).floor("min")

            text = str(value).strip().lower()

            try:
                # Relative minutes: "1 წუთის წინ"
                if 'წუთ' in text:
                    minutes = int(re.search(r'\d+', text).group())
                    return now - timedelta(minutes=minutes)

                # Relative hours: "23 საათის წინ"
                if 'საათ' in text:
                    hours = int(re.search(r'\d+', text).group())
                    return now - timedelta(hours=hours)

                parts = text.replace(',', '').split()

                # Full date with year: "01 იან 2026"
                if len(parts) == 3 and parts[2].isdigit():
                    day, geo_month, year = parts
                    month = self.geo_months.get(geo_month[:3])
                    if not month:
                        return pd.NA
                    return datetime(int(year), month, int(day), 12, 0)

                # Date + time without year: "30 დეკ 12:02"
                if len(parts) == 3 and ':' in parts[2]:
                    day, geo_month, time_str = parts
                    month = self.geo_months.get(geo_month[:3])
                    if not month:
                        return pd.NA

                    hour, minute = map(int, time_str.split(':'))
                    candidate = datetime(year=now.year, month=month, day=int(day), hour=hour, minute=minute)

                    # Handles year rollover
                    if candidate > now:
                        candidate = candidate.replace(year=now.year - 1)

                    return candidate

            except Exception:
                return pd.NA

            return pd.NA

        self.apartments_df['upload_date'] = (
            self.apartments_df['upload_date']
            .apply(parse_date).astype('datetime64[ns]').dt.floor('min')
        )

    def _normalize_transaction_type(self):
        """ Extracts transaction type from description.
            Possible values: იყიდება, ქირავდება თვიურად, ქირავდება დღიურად, გირავდება
        """

        def extract_transaction_type(desc):
            if pd.isna(desc):
                return pd.NA

            text = str(desc).lower()

            if "ქირავდება დღიურად" in text:
                return "ქირავდება დღიურად"
            if "ქირავდება" in text:
                return "ქირავდება თვიურად"
            if "იყიდება" in text:
                return "იყიდება"
            if "გირავდება" in text:
                return "გირავდება"

            return pd.NA

        self.apartments_df['transaction_type'] = (self.apartments_df['description'].
                                                  apply(extract_transaction_type).astype('string'))

    def _normalize_source(self):
        """ Extracts Source from url.
            Possible values: myhome.ge, livo.ge, home.ss.ge
        """

        def extract_source(url):
            if not isinstance(url, str):
                return pd.NA
            if "myhome.ge" in url:
                return "myhome.ge"
            if "livo.ge" in url:
                return "livo.ge"
            if "home.ss.ge" in url or "ss.ge" in url:
                return "home.ss.ge"
            return pd.NA

        self.apartments_df["source"] = self.apartments_df["url"].apply(extract_source)

    def write_to_csv(self, path=paths.APARTMENTS_PROCESSED_PATH):
        """ Writes the dataset to a csv file. """
        if self.apartments_df.empty:
            print(f"No data to write After Performing Data Cleaning")
            return
        self.apartments_df.to_csv(path, index=False, na_rep='<NA>')

    def normalize(self):
        self.__get_shape()
        self.__get_info()
        self.__get_description()
        self.__get_null_columns()

        self._normalize_price()
        self._normalize_area_m2()
        self._normalize_price_per_sqm()

        self._normalize_bedrooms()
        self._normalize_floor()

        self._normalize_upload_date()
        self._normalize_transaction_type()
        self._normalize_source()

        normalize_districts = NormalizeDistricts(self.apartments_df)
        normalize_districts.normalize_non_tbilisi_districts()
        normalize_districts.normalize_tbilisi_districts()
        self.apartments_df = normalize_districts.apartments_df
