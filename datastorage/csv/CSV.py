import pandas as pd
from config import paths


class CSV:
    def __init__(self):
        self.csv_path = paths.APARTMENTS_CSV_PATH
        self.write_from_csv = paths.APARTMENTS_PROCESSED_PATH

    def deduplicate_and_write(self) -> None:
        # Load new cleaned data
        new_df = pd.read_csv(self.write_from_csv)

        # Load existing data if it exists
        if self.csv_path.exists():
            old_df = pd.read_csv(self.csv_path)
            before_len = len(old_df)
            df = pd.concat([old_df, new_df], ignore_index=True)
        else:
            before_len = 0
            df = new_df

        # Deduplicate
        df = df.dropna(subset=["url"])
        df = df.drop_duplicates(subset="url", keep="last")

        after_len = len(df)

        # Reporting
        print(f"CSV | apartments rows: {after_len}")
        if after_len == before_len:
            return

        # Write back
        df.to_csv(self.csv_path, index=False)
