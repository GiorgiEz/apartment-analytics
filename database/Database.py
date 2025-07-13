import pandas as pd
import sqlite3


class Database:
    def __init__(self):
        self.apartments_table_name = 'apartments'
        self.db_path = 'database/apartments.db'

    def __create_table_if_not_exists(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.apartments_table_name} (
                url TEXT PRIMARY KEY,
                city TEXT,
                price INTEGER,
                price_per_sqm INTEGER,
                description TEXT,
                district_name TEXT,
                street_address TEXT,
                area_m2 REAL,
                upload_date TEXT,
                transaction_type TEXT
            );
        """)
        conn.commit()
        conn.close()

    def __insert_unique_csv_to_sqlite(self, csv_path):
        df = pd.read_csv(csv_path)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for _, row in df.iterrows():
            cursor.execute(f"""
                INSERT OR IGNORE INTO {self.apartments_table_name} (
                    url, city, price, price_per_sqm, description,
                    district_name, street_address, area_m2, upload_date, transaction_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(row))

        conn.commit()
        conn.close()

    def __apartments_table_length(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {self.apartments_table_name}")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def setup_database(self):
        self.__create_table_if_not_exists()
        self.__insert_unique_csv_to_sqlite("data_output/cleaned_apartments.csv")

        print(f"Length of the Apartments table in the sqlite database: {self.__apartments_table_length()}")
