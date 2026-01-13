import pandas as pd
from config import paths
from datetime import datetime


class CSV:
    def __init__(self):
        self.csv_path = paths.APARTMENTS_CSV_PATH
        self.backups_dir = paths.APARTMENTS_CSV_BACKUPS_DIR

    def backup(self):
        """
        Create a timestamped backup of the current apartments CSV
        before any modification.
        """
        if not self.csv_path.exists():
            return  # nothing to back up

        self.backups_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backups_dir / f"apartments_{timestamp}.csv"

        df = pd.read_csv(self.csv_path)
        df.to_csv(backup_path, index=False)

    def cleanup_old_backups(self, keep_last=20):
        backups = sorted(self.backups_dir.glob("apartments_*.csv"))
        for old in backups[:-keep_last]:
            old.unlink()

    def deduplicate_and_write(self, write_from_path=paths.APARTMENTS_PROCESSED_PATH) -> None:
        self.backup()
        self.cleanup_old_backups()
        # Load new cleaned data
        new_df = pd.read_csv(write_from_path)

        # Load existing data if it exists
        if self.csv_path.exists():
            old_df = pd.read_csv(self.csv_path)
            before_len = len(old_df)
            df = pd.concat([old_df, new_df], ignore_index=True)
        else:
            before_len = 0
            df = new_df

        # Deduplicate
        df = df.dropna(subset="url")
        df = df.drop_duplicates(subset="url", keep="last")

        after_len = len(df)

        # Reporting
        print(f"CSV | apartments rows: {after_len}")
        if after_len == before_len:
            return

        # Write back
        df.to_csv(self.csv_path, index=False)
