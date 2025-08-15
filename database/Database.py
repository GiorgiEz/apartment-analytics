import pandas as pd
import sqlite3, os, shutil
from datetime import datetime, timedelta


class Database:
    def __init__(self):
        self.apartments_table_name = 'apartments'
        self.db_path = 'database/apartments.db'
        self.backup_folder = 'backups'
        self.backup_retention_days = 30  # Keep backups for 30 days

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
                bedrooms INTEGER,
                floor INTEGER,
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
                    district_name, street_address, area_m2, bedrooms, floor, upload_date, transaction_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(row))

        conn.commit()
        conn.close()

    def __backup_database(self):
        """Creates a timestamped backup if DB changed"""
        if not os.path.exists(self.db_path):
            print("No database file found to backup.")
            return

        os.makedirs(self.backup_folder, exist_ok=True)

        # Compare with latest backup
        db_mod_time = os.path.getmtime(self.db_path)
        backups = sorted([f for f in os.listdir(self.backup_folder) if f.endswith(".db")], reverse=True)

        if backups:
            latest_backup_path = os.path.join(self.backup_folder, backups[0])
            latest_backup_mod_time = os.path.getmtime(latest_backup_path)
            print(f"{db_mod_time} - {latest_backup_mod_time}")
            if db_mod_time == latest_backup_mod_time:
                print("Database has not changed since last backup. Skipping backup.")
                return

        # Create new backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(self.backup_folder, f"apartments_backup_{timestamp}.db")
        shutil.copy2(self.db_path, backup_path)
        print(f"Backup created: {backup_path}")

    def __delete_old_backups(self):
        """Deletes backups older than retention period."""
        if not os.path.exists(self.backup_folder):
            return

        cutoff_time = datetime.now() - timedelta(days=self.backup_retention_days)
        for file in os.listdir(self.backup_folder):
            file_path = os.path.join(self.backup_folder, file)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_time < cutoff_time:
                    os.remove(file_path)
                    print(f"Deleted old backup: {file_path}")

        else:
            print("No backups older than retention period.")

    def __apartments_table_length(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {self.apartments_table_name}")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def setup_database(self):
        self.__delete_old_backups()  # Always clean old backups
        self.__backup_database()
        self.__create_table_if_not_exists()
        self.__insert_unique_csv_to_sqlite("data_output/cleaned_apartments.csv")

        print(f"Length of the Apartments table in the sqlite database: {self.__apartments_table_length()}")
