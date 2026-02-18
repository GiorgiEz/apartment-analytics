import pandas as pd
import os
from config import paths


class ApartmentsDataFrame:
    """Singleton class to manage a single DataFrame of all apartments """

    _instance = None

    def __new__(cls, livo_apartments_csv=paths.LIVO_APARTMENTS_RAW_PATH,
                myhome_apartments_csv=paths.MYHOME_APARTMENTS_RAW_PATH,
                sshome_apartments_csv=paths.SSHOME_APARTMENTS_RAW_PATH):
        """Ensures only one instance is created."""
        if cls._instance is None:
            cls._instance = super(ApartmentsDataFrame, cls).__new__(cls)
            cls._instance.init_data([livo_apartments_csv, myhome_apartments_csv, sshome_apartments_csv])
        return cls._instance

    def safe_read_csv(self, path):
        """Safely load a CSV file. Skip if missing, empty, or invalid."""
        if not os.path.exists(path):
            print(f"[WARN] File not found: {path}. Skipping.")
            return None

        if os.path.getsize(path) == 0:
            print(f"[WARN] File is empty: {path}. Skipping.")
            return None

        try:
            df = pd.read_csv(path)
            if df.empty:
                print(f"[WARN] File has no rows: {path}. Skipping.")
                return None
            return df
        except pd.errors.EmptyDataError:
            print(f"[WARN] No columns to parse in: {path}. Skipping.")
            return None
        except Exception as e:
            print(f"[WARN] Failed to read {path}: {e}. Skipping.")
            return None

    def init_data(self, csv_files):
        """Loads data from CSV files and merges them into a single DataFrame."""
        dfs = []

        for csv_path in csv_files:
            df = self.safe_read_csv(csv_path)
            if df is not None:
                dfs.append(df)

        if not dfs:
            print("[ERROR] No valid CSV files loaded. Creating empty DataFrame.")
            self.df = pd.DataFrame()
        else:
            self.df = pd.concat(dfs, ignore_index=True)

        print(f"DataFrame loaded with {len(self.df)} records.")

    def get_df(self):
        """Returns the DataFrame instance."""
        return self.df
